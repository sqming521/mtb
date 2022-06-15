import time
import datetime
import json
import requests

from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from utils.extension.mixins import MtbCreateModelMixin, MtbDestroyModelMixin
from utils.extension import return_code
from utils.token import get_authorizer_access_token
from ..serializers.message import ServiceMessageSerializer
from .. import models






class ServiceMessageView(MtbCreatgeModelMixin, GenericViewSet):
    """ 客户消息接口 """
    queryset = models.Message.objects.order_by('-id')
    serializer_class = ServiceMessageSerializer

    def perform_create(self, serializer):
        """ 序列化: 队请求的数据校验成功后，执行保存 """
        mtb_user_id = self.request.user.user_id
        public_object = serializer.validated_data["public"]

        # 1.校验图片和文本， 至少选择一项
        content = serializer.validated_data["content"]
        img = serializer.validated_data["img"]
        if not content and not img:
            serializer._error['content'] = ["文本和图片至少选择一项",]
            return Response({"code": return_code.FIELD_ERROR, 'detail': serializer.errors})

        # 2. 如果有图片， 上传图片到微信的素材库
        media_id = None
        if img:
            authorizer_access_token = get_authorizer_access_token(public_object)
            # 调用微信接口
            res = requests.post(
                url="https://api.weixin.qq.com/cgi-bin/material/add_material",
                params={
                    "access_token": authorizer_access_token,
                    "type": "image"
                },
                files={
                    "media": (
                        'message-{}-{}.png'.format(public_object.authorizer_app_id, int(time.time() * 1000)),
                        open(img[1:], mode='rb'),   #去掉开头的/，这样不会从根目录开始找
                        "image/png"
                    )
                },
            )
            media_id = res.json()['media_id']

        # 3.数据库中新建记录
        instance = serializer.save(
            mtb_user_id=mtb_user_id,
            msg_type=2,
            media_id=media_id
        )
import time
import importlib
import xml.etree.cElementTree as ET

import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.urls import reverse
from django.http import FileResponse, HttpResponse
from django.conf import settings
from django.shortcuts import redirect

from utils.wx2.WXBizMsgCrypt import WXBizMsgCrypt
from utils.extension import return_code
from utils.extension.auth import ParamsJwtTokenAuthentication
from .. import models
from ..serializers.wx import PublicNumberSerializer
from utils.extension.mixins import MtbListModelMixin
from utils.extension.filters import SelfFilterBackend

def file_verify(requset, filename):
    file = open('', 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s.txt"' % filename
    return response


def component_verify_ticket(request):
    """ 微信每隔10分钟以POST请求发送一次 """
    if request.method != 'POST':
        return HttpResponse("error")
    # 获取请求体数据
    body = request.body.decode('utf-8')

    # 获取URL中的数据
    nonce = request.GET.get('nonce')
    timestamp = request.GET.get('timestamp')
    msg_sign = request.GET.get('msg_signature')

    # 解密 需安装第三方模块 pycryptodome
    decrypt_test = WXBizMsgCrypt(settings.WX_TOKEN, settings.WX_KEY, settings.WX_APP_ID)
    # 解密得到的是状态码和一个xml配置文件
    code, decrypt_xml = decrypt_test.DecryptMsg(body, msg_sign, timestamp, nonce)

    # code=0时 解密成功
    if code != 0:
        return HttpResponse('error')
    print(decrypt_xml)
    # 得到的decrypt_xml格式如下
    """
        这是
        <xml>
            <AppId><![CDATA[wx89d0d065c7b25a06]]></AppId>
            <CreateTime>1648305909</CreateTime>
            <InfoType><![CDATA[component_verify_ticket]]></InfoType>
            <ComponentVerifyTicket><![CDATA[ticket@@@fAovP2Qo9vbcdJ_O6sw6r2APV2jTQZJkeV73OBnazo6rTDhC85I8ywcY_wqXhthC5AFRNHg_aNuiAl7xljFf-w]]></ComponentVerifyTicket>
        </xml>
        <xml>
            微信公众号取消授权
    	    <AppId><![CDATA[wx89d0d065c7b25a06]]></AppId>
            <CreateTime>1648455334</CreateTime>
            <InfoType><![CDATA[unauthorized]]></InfoType>
            <AuthorizerAppid><![CDATA[wx75cd30b4c2693497]]></AuthorizerAppid>
        </xml>
        """
    xml_tree = ET.fromstring(decrypt_xml)

    info_type = xml_tree.find('InfoType')
    if info_type == 'component_verify_ticket':
        verify_ticket = xml_tree.find('ComponentVerifyTicket')
        verify_ticket_text = verify_ticket.text
        # 写入数据库(过期时间12h)
        period_time = int(time.time()) + 12 * 60 * 60
        # 不存在: 增;存在: 更新
        models.WxCode.objects.update_or_create(defaults={"value": verify_ticket, "period": period_time}, code_type=1)
        return HttpResponse('success')

    if info_type == 'unauthorized':
        # 本质: 删除数据库中已授权的公众号
        authorizer_app_id = xml_tree.find('AuthorizerAppid').text
        models.PublicNumbers.objects.filter(authorizer_app_id=authorizer_app_id).delete()
        return HttpResponse('success')

    return HttpResponse('success')


class WxUrlView(APIView):

    def create_component_access_token(self):
        """ 根据 component_verify_ticket 生成新的component_access_token(有效期两小时)并写入数据库"""
        verify_ticket_object = models.WxCode.objects.filter(code_type=1).first()
        # requests.post：向url发送post请求并获取响应文本
        res = requests.post(
            url="https://api.weixin.qq.com/cgi-bin/component/api_component_token",
            json={
                "component_appid": settings.WX_APP_ID,
                "component_appsecret": settings.WX_APP_SECRET,
                "component_verify_ticket": verify_ticket_object.value
            }
        )
        data_dict = res.json()

        access_token = data_dict['component_access_token']
        period_time = int(data_dict['expires_in']) + int(time.time())  # 获取过期时间

        models.WxCode.objects.update_or_create(defaults={"value": access_token, "period": period_time}, code_type=2)
        return access_token

    def create_pre_auth_code(self, access_token):
        # 生成预授权码
        res = requests.post(
            url="https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode",
            params={
                "component_access_token": access_token
            },
            json={
                "component_appid": settings.WX_APP_ID
            }
        )

        data_dict = res.json()
        pre_auth_code = data_dict["pre_auth_code"]
        period_time = int(data_dict['expires_in']) + int(time.time())
        models.WxCode.objects.update_or_create(defaults={"value": pre_auth_code, "period_time": period_time},
                                               code_type=3)
        return pre_auth_code

    def create_qr_code_url(self, pre_auth_code, jwt_token):
        redirect_uri = "{}{}?token={}".format("http://www.anpufeibo.com", reverse("wx_callback"), jwt_token)
        auth_url = "https://mp.weixin.qq.com/cgi-bin/componentloginpage?component_appid={}&pre_auth_code={}&redirect_uri={}&auth_type=1"
        target_url = auth_url.format(settings.WX_APP_ID, pre_auth_code, redirect_uri)
        return target_url

    def get(self, request, *args, **kwargs):
        """ 生成URL并返回，用户跳转到微信扫码授权页面 """

        # 去数据库获取预授权码(10分钟有效期)
        pre_auth_code_object = models.WxCode.objects.filter(code_type=3).first()
        pre_exp_time = pre_auth_code_object.period if pre_auth_code_object else 0

        # 预授权码还在有效期，则直接生成URL返回
        if int(time.time()) < pre_exp_time:
            url = self.create_qr_code_url(pre_auth_code_object.value, request.auth)
            return Response({"code": return_code.SUCCESS, "data": {"url": url}})

        # 根据 component_verify_ticket 获取 component(有效期2小时)
        access_token_object = models.WxCode.objects.filter(code_type=2).first()
        expiration_time = access_token_object.period if access_token_object else 0
        if int(time.time()) >= expiration_time:
            # 已过期或没有
            access_token = self.create_component_access_token()
        else:
            # 未过期
            access_token = access_token_object.value

        # 根据 component_access_token 生成预授权码 pre_auth_code(有效期十分钟)
        pre_auth_code = self.create_pre_auth_code(access_token)

        url = self.create_qr_code_url(pre_auth_code, request.auth)
        return Response({"code": return_code.SUCCESS, "data": {"url": url}})


class WxCallBackView(APIView):
    authentication_classes = [ParamsJwtTokenAuthentication]

    def create_component_access_token(self):
        """ 根据 component_verify_ticket 生成新的component_access_token(有效期两小时)并写入数据库"""
        verify_ticket_object = models.WxCode.objects.filter(code_type=1).first()
        # requests.post：向url发送post请求并获取响应文本
        res = requests.post(
            url="https://api.weixin.qq.com/cgi-bin/component/api_component_token",
            json={
                "component_appid": settings.WX_APP_ID,
                "component_appsecret": settings.WX_APP_SECRET,
                "component_verify_ticket": verify_ticket_object.value
            }
        )
        data_dict = res.json()

        access_token = data_dict['component_access_token']
        period_time = int(data_dict['expires_in']) + int(time.time())  # 获取过期时间

        models.WxCode.objects.update_or_create(defaults={"value": access_token, "period": period_time}, code_type=2)
        return access_token

    def get(self, request, *args, **kwargs):
        # # http://mtb.pythonav.com/api/base/wxcallback/?auth_code=queryauthcode@@@4w8n0KmfmOZ-21X_UqC6aOCEQ6Yrck-UD5c9Wn_5cRfoK8VAvg0Z-1K9bBXMl9EuJ-Xv7A0qA6nPSxfci3DQkQ&expires_in=3600
        auth_code = request.GET.get("auth_code")
        expires_in = request.GET.get("expires_in")
        print(auth_code, expires_in)

        # request.user -> 我们系统的已登录用户   授权码 auth_code

        # 1.根据 auth_code 获取 authorizer_access_token （authorizer_refresh_token）+ 过期
        # 1.1 获取 component_access_token（2小时）
        access_token_object = models.WxCode.objects.filter(code_type=2).first()
        expiration_time = access_token_object.period if access_token_object else 0
        if int(time.time()) >= expiration_time:
            # 已过期或者没有
            access_token = self.create_component_access_token()
        else:
            # 未过期
            access_token = access_token_object.value

        # 1.2 发送请求authorizer_access_token
        res = requests.post(
            url="https://api.weixin.qq.com/cgi-bin/component/api_query_auth",
            params={
                "component_access_token": access_token,
            },
            json={
                "component_appid": settings.WX_APP_ID,
                "authorization_code": auth_code,
            }
        )
        result = res.json()
        # 公众号的appid及token
        authorizer_appid = result['authorization_info']['authorizer_appid']
        authorizer_access_token = result['authorization_info']['authorizer_access_token']
        authorizer_refresh_token = result['authorization_info']['authorizer_refresh_token']
        authorizer_period = int(result['authorization_info']['expires_in']) + int(time.time())

        # 2.公众号基本信息：头像、名称（authorizer_access_token / component_access_token ）
        res = requests.post(
            url="https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info",
            params={
                "component_access_token":access_token
            },
            json={
                "component_appid": settings.WX_APP_ID,
                "authorizer_appid": authorizer_appid
            },
        ).json()

        nick_name = res["authorizer_info"]["nick_name"]
        user_name = res["authorizer_info"]["user_name"]  # 原始ID
        avatar = res["authorizer_info"]["head_img"]
        service_type_info = res["authorizer_info"]["service_type_info"]["id"]
        verify_type_info = res["authorizer_info"]["verify_type_info"]["id"]

        # 3.保存起来 -> 用户相关（新增、更新）   平台用户ID + 原始ID （user_name）
        models.PublicNumbers.objects.update_or_create(
            defaults={
                "authorizer_app_id": authorizer_appid,
                "authorizer_access_token": authorizer_access_token,
                "authorizer_refresh_token": authorizer_refresh_token,
                "authorizer_period": authorizer_period,  # 2小时

                "nick_name": nick_name,
                "avatar": avatar,
                "service_type_info": service_type_info,
                "verify_type_info": verify_type_info,
            },
            mtb_user_id = request.user.user_id,
            user_name = user_name
        )

        return redirect('http://www.anpufeibo.top:8000/auth')

class PublicNumberView(MtbListModelMixin,GenericViewSet):
    """ 我的公众号列表 """
    filter_backends = [SelfFilterBackend, ]
    queryset = models.PublicNumbers.objects.order_by("-id")

    serializer_class = PublicNumberSerializer

def event_callback(request, authorizer_app_id):
    """ 公众号的消息与实践接收配置 """
    if request.method != "POST":
        return HttpResponse('error')
    # 获取请求体数据
    body = request.body.decode('utf-8')

    # 获取URL中的数据
    nonce = request.GET.get('nonce')
    timestamp = request.GET.get('timestamp')
    msg_sign = request.GET.get('msg_signature')

    # 解密 pip install pycryptodomo
    decrypt_test = WXBizMsgCrypt(settings.WX_TOKEN, settings.WX_KEY, settings.WX_APP_ID)
    code, decrypt_xml = decrypt_test.DecryptMsg(body, msg_sign, timestamp, nonce)

    # code=0时解密成功
    if code != 0:
        return HttpResponse('error')
    print(authorizer_app_id, decrypt_xml)

    event_list = {
        "apps.msg.event.handler"
        "apps.task.event.handler"
    }
    for path in event_list:
        module_path, func_name = path.rsplit('.', maxsplit=1)
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)
        func(authorizer_app_id, decrypt_xml)

    return HttpResponse('success')

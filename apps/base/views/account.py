import datetime

import jwt
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

from utils.extension import return_code
from ..serializers.account import AuthSerializer
from .. import models


class AuthView(APIView):
    '''用户登录'''
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):

        # 1. 表单验证，用户名密码不能为空
        serializer = AuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"code": return_code.VALIDATE_ERROR, 'detail': serializer.errors})

        # 2.数据库查询
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        user_object = models.UserInfo.objects.filter(username=username, password=password).first()
        if not user_object:
            return Response({"code": return_code.VALIDATE_ERROR, 'error': "用户名或密码错误"})

        # 登陆成功，生成token
        headers = {
            'typ': "jwt",
            'alg': 'HS256'
        }

        payload = {
            'user_id': user_object.id,
            'username': user_object.username,
            "exp": datetime.datetime.now() + datetime.timedelta(days=7)
        }
        jwt_token = jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm="HS256", headers=headers)

        return Response({"code": return_code.SUCCESS, "data": {"token": jwt_token, "name": user_object.username}})


class TestView(APIView):
    def get(self, request, *args, **kwargs):
        print(request.user.user_id)
        print(request.user.username)
        print(request.user.exp)
        return Response('test')
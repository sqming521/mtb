import jwt

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from . import return_code


class CurrentUser:
    def __init__(self, user_id, username, exp):
        self.user_id = user_id
        self.username = username
        self.exp = exp


class JwtTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # 读取用户提交的jwt token
        token = request.query_params.get('token')

        if not token:
            raise AuthenticationFailed({'code': return_code.AUTH_FAILED, 'error': "认证失败"})
        # jwt token的校验
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, ["HS256"])
            print(type(payload), payload)
            return CurrentUser(**payload),token
        except Exception as e:
            print(e)
            raise AuthenticationFailed({'code': return_code.AUTH_FAILED, 'error': "认证失败"})

    def authenticate_header(self, request):
        return 'Bearer realm="API"'
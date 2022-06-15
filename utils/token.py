import time
import requests
from apps.base import models
from django.conf import settings


def create_component_access_token():
    """ 根据 component_verify_ticket 生成新的component_access_token并写入数据库"""
    verify_ticket_object = models.WxCode.objects.filter(code_type=1).first()

    res = requests.post(
        url="https://api.weixin.qq.com/cgi-bin/component/api_component_token",
        json={
            "component_appid": settings.WX_APP_ID,
            "component_appsecret": settings.WX_APP_SECRET,
            "component_verify_ticket": verify_ticket_object.value
        }
    )
    data_dict = res.json()
    access_token = data_dict["component_access_token"]
    period_time = int(data_dict["expires_in"]) + int(time.time())
    models.WxCode.objects.update_or_create(defaults={"value": access_token, "period": period_time}, code_type=2)
    return access_token


def get_component_access_token():
    access_token_object = models.WxCode.objects.filter(code_type=2).first()
    expiration_time = access_token_object.period if access_token_object else 0
    if int(time.time()) >= expiration_time:
        # 已过期或没有
        access_token = create_component_access_token()
    else:
        # 未过期
        access_token = access_token_object.value
    return access_token


def get_authorizer_access_token(pub_object):
    ctime = int(time.time())
    if ctime < pub_object.authorizer_period:
        return pub_object.authorizer_access_token


    # 根据authorizer_refresh_token获取最新的token 并写入数据库
    component_access_token = get_component_access_token()
    res = requests.post(
        url="https://api.weixin.qq.com/cgi-bin/component/api_authorizer_token",
        params={
            "component_access_token": component_access_token,
        },
        json={
            "component_appid": settings.WX_APP_ID,
            "authorizer_appid": pub_object.authorizer_app_id,
            "authorizer_refresh_token": pub_object.authorizer_refresh_token
        }
    )
    data_dict = res.json()

    # print(data_dict)

    pub_object.authorizer_access_token = data_dict["authorizer_access_token"]
    pub_object.authorizer_refresh_token = data_dict['authorizer_refresh_token']
    pub_object.authorizer_period = int(time.time()) + data_dict['expires_in']
    pub_object.save()

    return data_dict["authorizer_access_token"]

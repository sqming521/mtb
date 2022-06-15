from django.db import models

# Create your models here.


class WxCode(models.Model):
    """ 微信授权相关的码 """
    code_type_choices = (
        (1, "component_verify_ticket"),
        (2, "component_access_token"),
        (3, "pre_auth_code")
    )

    code_type = models.IntegerField(verbose_name="类型", choices=code_type_choices)

    # value = models.CharField(verbose_name="值", max_length=128)
    value = models.CharField(verbose_name="值", max_length=256)
    period = models.PositiveIntegerField(verbose_name="过期时间")

class UserInfo(models.Model):
    username = models.CharField(verbose_name='用户名',max_length=32)
    password = models.CharField(verbose_name='密码' ,max_length=32)



class PublicNumbers(models.Model):
    authorizer_app_id = models.CharField(verbose_name="授权ID", max_length=64)
    authorizer_access_token = models.CharField(verbose_name="授权token", max_length=255)
    authorizer_refresh_token = models.CharField(verbose_name="授权更新token", max_length=64)
    authorizer_period = models.PositiveIntegerField(verbose_name="过期时间")

    nick_name = models.CharField(verbose_name='公众号名称', max_length=32)
    user_name = models.CharField(verbose_name='公众号原始ID', max_length=64)
    avatar = models.CharField(verbose_name='公众号头像', max_length=128)
    service_type_info = models.IntegerField(
        verbose_name="公众号类型",
        choices=(
            (0, "订阅号"),
            (1, "由历史老帐号升级后的订阅号"),
            (2, "服务号")
        )
    )
    verify_type_info = models.IntegerField(
        verbose_name='认证类型',
        choices=(
            (-1, "未认证"),
            (0, "微信认证"),
            (1, "新浪微博认证"),
            (2, "腾讯微博认证"),
            (3, "已资质认证通过但还未通过名称认证"),
            (4, "已资质认证通过、还未通过名称认证，但通过了新浪微博认证"),
            (5, "已资质认证通过、还未通过名称认证，但通过了腾讯微博认证"),
        )
    )

    mtb_user = models.ForeignKey(verbose_name='媒体宝用户',to='UserInfo',on_delete=models.CASCADE)
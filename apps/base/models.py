from django.db import models

# Create your models here.


class WxCode(models.Model):
    """ 微信授权相关的码 """
    code_type_choices = (
        (1, "component_verify_ticket"),
    )

    code_type = models.IntegerField(verbose_name="类型", choices=code_type_choices)

    # value = models.CharField(verbose_name="值", max_length=128)
    value = models.CharField(verbose_name="值", max_length=256)
    period = models.PositiveIntegerField(verbose_name="过期时间")

class UserInfo(models.Model):
    username = models.CharField(verbose_name='用户名',max_length=32)
    password = models.CharField(verbose_name='密码' ,max_length=32)
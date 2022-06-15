from django.db import models

# Create your models here.
class Interaction(models.Model):
    """ 互动表，用于记录最近48小时内有互动的人 """
    authorizer_app_id = models.CharField(verbose_name='公众号授权ID', max_length=64)
    user_open_id = models.CharField(max_length=64, verbose_name='互动粉丝ID')
    end_date = models.PositiveIntegerField(verbose_name='互动戒指时间戳', help_text="互动时间+48小时")


class Message(models.Model):
    """ 消息表 """
    mtb_user = models.ForeignKey(verbose_name="创建者", to="base.UserInfo", on_delete=models.CASCADE)

    msg_type = models.IntegerField(verbose_name="消息类型", choices=((1, "模板消息"),(2, "客户消息")))

    public = models.ForeignKey(verbose_name="公众号", to="base.PublicNumbers",on_delete=models.CASCADE)
    title = models.CharField(max_length=64, verbose_name='标题')

    # 模板消息
    template_id = models.CharField(verbose_name='模板ID', max_length=128)

    # 客户消息
    img = models.CharField(max_length=128, verbose_name='图片', null=True, blank=True)
    media_id = models.CharField(max_length=64, verbose_name="微信媒体ID", null=True,blank=True)

    content = models.TextField(verbose_name='发送内容', blank=True, null=True)

    interaction = models.IntegerField(
        verbose_name="48小时互动",
        choices=((1, "48小时互动"), (2, "不限")),
        default=1
    )

    task_id = models.CharField(max_length=64, verbose_name='Celery任务ID')
    status = models.IntegerField(
        verbose_name="任务状态",
        choices=((1, '待发送'),(2, '发送中'), (3, "已完成")),
        default=1
    )

    count = models.IntegerField(verbose_name='发送数量', default=0, blank=True)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


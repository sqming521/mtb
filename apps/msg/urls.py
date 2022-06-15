from django.urls import path
from rest_framework import routers

from .views import message
# from .views import template

router = routers.SimpleRouter()

# 客服消息接口
router.register(r'service/message', message.ServiceMessageView)
# 模板消息接口
# router.register(r'template/message', message.TemplateMessageView)
# 消息展示接口
# router.register(r'message', message.MessageView)

# SOP
# 添加
# router.register(r'template/sop', message.TemplateSopView)

# 查看SOP列表数据/删除SOP数据
# router.register(r'sop', message.SopView)

urlpatterns = [
    # path('auth/', account.AuthView.as_view()),
    # 根据公众号获取所有的消息模板
    # path('template/', template.TemplateView.as_view()),
]

urlpatterns += router.urls

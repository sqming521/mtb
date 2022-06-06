"""mtb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from rest_framework import routers
from .views import account

router = routers.SimpleRouter()

# 评论
# router.register(r'comment', comment.CommentView)
urlpatterns = [
    path('auth/',account.AuthView.as_view()),
    path('test/',account.TestView.as_view()),
]

urlpatterns += router.urls
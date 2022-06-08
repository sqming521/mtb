import time
import xml.etree.cElementTree as ET

from django.http import FileResponse,HttpResponse
from django.conf import settings
from utils.wx2.WXBizMsgCrypt import WXBizMsgCrypt
from .. import models


def file_verify(requset,filename):
    file = open('','rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s.txt"' %filename
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

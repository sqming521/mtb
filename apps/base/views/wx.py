import time
import xml.etree.cElementTree as ET

from django.http import FileResponse, HttpResponse
from django.conf import settings
from utils.wx2.WXBizMsgCrypt import WXBizMsgCrypt
from .. import models


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
    code, decrypt_xml = decrypt_test.DecryptMsg(body, msg_sign, timestamp, nonce)
    # 解密得到的是状态码和一个xml配置文件
    if code != 0:
        return HttpResponse('error')
    print(decrypt_xml)
    # 得到的decrypt_xml格式如下
    """
        <xml>
            <AppId><![CDATA[wx89d0d065c7b25a06]]></AppId>
            <CreateTime>1648305909</CreateTime>
            <InfoType><![CDATA[component_verify_ticket]]></InfoType>
            <ComponentVerifyTicket><![CDATA[ticket@@@fAovP2Qo9vbcdJ_O6sw6r2APV2jTQZJkeV73OBnazo6rTDhC85I8ywcY_wqXhthC5AFRNHg_aNuiAl7xljFf-w]]></ComponentVerifyTicket>
        </xml>
        <xml>
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
        models.WxCode.objects.update_or_create(defaults={"value": verify_ticket,"period":period_time},code_type=1)
        return HttpResponse('success')
import time
import xml.etree.cElementTree as ET
from . import models


def handler(authorizer_app_id, decrypt_xml):
    """ 接收信息 """
    xml_tree = ET.fromstring(decrypt_xml)
    msg_type = xml_tree.find("MsgType").text

    # 更新互动表
    if msg_type in {"text", "image", "voice", "video"}:
        from_user_open_id = xml_tree.find("FromUserName").text
        models.Interaction.objects.update_or_create(
            defaults={"end_date": int(time.time()) + 48 * 60 *60},
            authorizer_app_id=authorizer_app_id,
            user_open_id=from_user_open_id,
        )
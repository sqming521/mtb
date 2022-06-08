#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# Author: jonyqin
# Created Time: Thu 11 Sep 2014 03:55:41 PM CST
# File Name: demo.py
# Description: WXBizMsgCrypt 使用demo文件
#########################################################################
from WXBizMsgCrypt import WXBizMsgCrypt

if __name__ == "__main__":
    """ 
    1.第三方回复加密消息给公众平台；
    2.第三方收到公众平台发送的消息，验证消息的安全性，并对消息进行解密。
    """
    #
    # encodingAESKey = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG"
    # to_xml = """ <xml><ToUserName><![CDATA[oia2TjjewbmiOUlr6X-1crbLOvLw]]></ToUserName><FromUserName><![CDATA[gh_7f083739789a]]></FromUserName><CreateTime>1407743423</CreateTime><MsgType>  <![CDATA[video]]></MsgType><Video><MediaId><![CDATA[eYJ1MbwPRJtOvIEabaxHs7TX2D-HV71s79GUxqdUkjm6Gs2Ed1KF3ulAOA9H1xG0]]></MediaId><Title><![CDATA[testCallBackReplyVideo]]></Title><Descript  ion><![CDATA[testCallBackReplyVideo]]></Description></Video></xml>"""
    # token = "spamtest"
    # nonce = "1320562132"
    # appid = "wx2c2769f8efd9abc2"
    # # 测试加密接口
    # # encryp_test = WXBizMsgCrypt(token,encodingAESKey,appid)
    # # ret,encrypt_xml = encryp_test.EncryptMsg(to_xml,nonce)
    # # print(ret,encrypt_xml)
    #
    # # 测试解密接口
    # timestamp = "1409735669"
    # msg_sign = "5d197aaffba7e9b25a30732f161a50dee96bd5fa"
    #
    # from_xml = """<xml><ToUserName><![CDATA[gh_10f6c3c3ac5a]]></ToUserName><FromUserName><![CDATA[oyORnuP8q7ou2gfYjqLzSIWZf0rs]]></FromUserName><CreateTime>1409735668</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[abcdteT]]></Content><MsgId>6054768590064713728</MsgId><Encrypt><![CDATA[hyzAe4OzmOMbd6TvGdIOO6uBmdJoD0Fk53REIHvxYtJlE2B655HuD0m8KUePWB3+LrPXo87wzQ1QLvbeUgmBM4x6F8PGHQHFVAFmOD2LdJF9FrXpbUAh0B5GIItb52sn896wVsMSHGuPE328HnRGBcrS7C41IzDWyWNlZkyyXwon8T332jisa+h6tEDYsVticbSnyU8dKOIbgU6ux5VTjg3yt+WGzjlpKn6NPhRjpA912xMezR4kw6KWwMrCVKSVCZciVGCgavjIQ6X8tCOp3yZbGpy0VxpAe+77TszTfRd5RJSVO/HTnifJpXgCSUdUue1v6h0EIBYYI1BD1DlD+C0CR8e6OewpusjZ4uBl9FyJvnhvQl+q5rv1ixrcpCumEPo5MJSgM9ehVsNPfUM669WuMyVWQLCzpu9GhglF2PE=]]></Encrypt></xml>"""
    # decrypt_test = WXBizMsgCrypt(token, encodingAESKey, appid)
    # ret, decryp_xml = decrypt_test.DecryptMsg(from_xml, msg_sign, timestamp, nonce)
    # print(ret, decryp_xml)
    token = "c32b4c29-ac7e-4ebc-b7f4-6125159bbf11"
    key = "a4537fb5112343a48bb9af33e8074d636125159bbf1"
    app_id = "wx89d0d065c7b25a06"
    app_secret = "e359cf673dae224e976d75d00dbec0a6"
    msg_sign = "298fb9709ed883080c0416e0c3a8bbb0c9a4ab8e"
    timestamp = "1599693928"
    nonce = "116852843"
    content = """<xml>
        <AppId><![CDATA[wx89d0d065c7b25a06]]></AppId>
        <Encrypt><![CDATA[HQL/0rbQVMRpc750zzH8avu6WDYF0BVDSBxPatBgxHxS273qGnBl/6QkwSeKuvBm6jNaKWM8vnbZ4D5j5wcoyNaggyfVEOowa5sJloGkZwRJpY/t/PUlCU5h/0Ectxdow6uMBSlfggwaw35Km4uJOhjYujDbF93+nPmee7RuJvTRg7RXH6zCZyt6VXsSxE3Rv2OsbW3Un6qRKolcRBUDWxgJFCmk0V2xrKttn1Jv8sKq6VYj4R1XU6Zmp0XUPdWwb1nHuhDthCxj9m/WV3YrTY3UHoq/jKs3/R6cRHAlliMqyVaVOCfoltp4r8Mm/nPu1E9QswqALPRhyaSpLJdoTp4uebvP/aylOla1Tmjm2dCcSRi8cMHE1lwBKN5NW9EILM03SuRVHkZLTH9QUH+wwvWOVAu7f/5ZVEI27b7BPDsPKgkOy2NpxcNwH1rO0G3dkV+r0+hFN5sCSwG/t+d01w==]]></Encrypt>
    </xml>"""

    decrypt_test = WXBizMsgCrypt(token.replace("\n", ""), key, app_id)
    ret, decryp_xml = decrypt_test.DecryptMsg(content, msg_sign, timestamp, nonce)
    print(ret, decryp_xml)

    import xml.etree.cElementTree as ET

    xml_tree = ET.fromstring(decryp_xml)
    ComponentVerifyTicket = xml_tree.find("ComponentVerifyTicket")
    print(ComponentVerifyTicket.text)

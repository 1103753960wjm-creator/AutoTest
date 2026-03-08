from email.mime.multipart import MIMEMultipart
import json
import smtplib
from email.mime.text import MIMEText
import time
import hmac
import hashlib
import base64
import urllib.parse

import requests

from config.settings import source_ip, report_ip
from views.api.api_model import Api_script_result_list


async def send_business(data, result_id, type):
    """
    发送微信群组机器人消息
    :param text: 消息内容
    :param webHookUrl: 群组机器人WebHook
    :param mentioned_list: userid的列表，提醒群中的指定成员(@某个成员)，@all表示提醒所有人
    :param mentioned_mobile_list: 手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人
    """
    try:
        webHookUrl = data["value"]

        if type == "_api":
            result = (
                await Api_script_result_list.filter(result_id=result_id)
                .first()
                .values()
            )
            total = result["result"]["total"]
            passed = result["result"]["pass"]
            failed = result["result"]["fail"]
            percent = result["result"]["percent"]
            text = {
                "msgtype": "markdown",
                "markdown": {
                    "content": f"{data['script']['msg']}\n运行总数：{total}个, 通过率：{percent}%\n通过的数量：<font color=\"info\">{passed}个</font>\n失败的数量：<font color=\"warning\">{failed}个</font>\n[>> 点击进入测试平台查看完整报告详情 <<]({report_ip}/{type}_report?result_id={result_id})"
                },
                "mentioned_list": ["@all"],  # @全体成员
            }
        else:
            text = {
                "msgtype": "news",
                "news": {
                    "articles": [
                        {
                            "title": data["script"]["msg"],
                            "description": "点击进入测试平台",
                            "url": f"{report_ip}/{type}_report?result_id={result_id}",
                            "picurl": f"{source_ip}/media/img/report_img.jpg",
                        }
                    ]
                },
            }
        headers = {"Content-Type": "application/json", "Charset": "UTF-8"}
        requests.post(webHookUrl, headers=headers, json=text)
        return True
    except Exception as e:
        print(f"企业微信机器人信息发送失败，原因是：{str(e)}")


async def sign_dingding():
    timestamp = str(round(time.time() * 1000))
    secret = "xxxxx"
    secret_enc = secret.encode("utf-8")
    string_to_sign = "{}\n{}".format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode("utf-8")
    hmac_code = hmac.new(
        secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    print(timestamp)
    print(sign)
    return timestamp, sign


async def send_dingding(data, result_id, type):
    """
    发送钉钉群组机器人消息
    :param text: 消息内容
    :param webHookUrl: 群组机器人WebHook
    Args:
        data:
    """
    try:
        # timestamp, sign = await sign_dingding()
        # webHookUrl = f"{data['value']}&timestamp={timestamp}&sign={sign}"
        webHookUrl = data["value"]
        print(webHookUrl)
        text = {
            "msgtype": "link",
            "link": {
                "text": data["script"]["msg"],
                "title": f"{type}定时任务结果通知",
                "picUrl": f"{source_ip}/media/img/report_img.jpg",
                "messageUrl": f"{report_ip}/{type}_report?result_id={result_id}",
            },
        }
        headers = {"Content-Type": "application/json"}
        res = requests.post(url=webHookUrl, headers=headers, data=json.dumps(text))
        print("钉钉通知结果：", res.text)
        return True
    except Exception as e:
        print(f"企业钉钉机器人信息发送失败，原因是：{str(e)}")


async def send_email(data, result_id, type):
    # QQ 邮箱的 SMTP 服务器配置
    smtp_server = "smtp.qq.com"
    smtp_port = 465

    # 发送方和接收方信息
    sender_email = data["script"]["email_from"]
    sender_password = data["script"][
        "email_password"
    ]  # 注意：这里是授权码，不是邮箱密码！
    values = [item for item in data["script"]["email_to"]]
    receiver_email = ",".join(values)
    # 创建邮件内容
    if type == "运维告警":
        subject = f"电话所有拨打失败-{type}通知"
        body = f"电话所有拨打失败-{type}通知"
    else:
        subject = f"{type} 定时任务结果通知"
        body = data["script"]["msg"]

    # 构建邮件
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # 添加邮件正文
    msg.attach(MIMEText(body, "plain"))

    try:
        # 连接到 SMTP 服务器
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)

        # 发送邮件
        server.sendmail(sender_email, receiver_email, msg.as_string())

        print(f"{subject}, 邮件发送成功！")
    except Exception as e:
        print(f"邮件发送失败: {e}")
    finally:
        server.quit()

from datetime import datetime
import time
from fastapi import Request
from fastapi import APIRouter
import requests

from common.device import device_info
from common.msg_notice_send import send_email
from common.paginate import db_page_all
from common.request_to_json import body_to_json
from common.return_code import catch_Exception, res_fail, res_success
from views.app.app_model import App_device
from views.warning_call.call_commom import assign_phones_to_devices, make_a_call
from views.warning_call.call_model import Call_list

router = APIRouter(prefix="/api/call")


@router.post("/call_phone")
async def call_phone(request: Request):
    try:
        body = await body_to_json(request)
        print(f"开始拨打电话：{body['phones']}")
        phone_device = [
            "手机号"
        ]
        fail_list = []
        success_dict, remaining_phones = assign_phones_to_devices(
            body["phones"], phone_device
        )
        for i in body["phones"]:
            if i not in str(success_dict):
                fail_list.append(i)
        if not success_dict:
            # 在这里可以执行邮件通知或者其他通知
            await Call_list.create(
                success_list={"msg": "所有电话拨通失败，已进行邮件通知"}
            )
            return await res_fail(f"所有电话拨通失败，已开启邮件通知")
        await Call_list.create(success_list=success_dict)
        return await res_success(success_dict)
    except Exception as e:
        return await res_fail(f"电话拨通失败，原因：{e}")

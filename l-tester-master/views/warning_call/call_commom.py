import asyncio
import json
import re
import subprocess
import time
import multiprocessing
from multiprocessing import Pool, Manager
from config.settings import report_ip, source_ip
import requests
from views.task.task_model import Msg_Notice


def assign_phone_to_device(args):
    """多进程任务：尝试绑定手机号"""
    phone, device, success_dict, failed_phones, failed_devices, lock = args

    # 新增：拨号前检查设备是否空闲
    time.sleep(2)
    if get_call_state(device):
        if make_a_call(phone, device):
            with lock:
                success_dict[device] = phone
                if phone in failed_phones:
                    failed_phones.remove(phone)
            return True
    else:
        print("设备%s正在被使用" % device)
        with lock:
            if device not in failed_devices:
                failed_devices.append(device)
        return False


def assign_phones_to_devices(phones, devices):
    """多进程分配手机号给设备"""
    manager = Manager()
    success_dict = manager.dict()
    failed_phones = manager.list(phones.copy())
    failed_devices = manager.list()
    lock = manager.Lock()
    while True:
        # 检查终止条件
        remaining_devices = len(devices) - len(success_dict) - len(failed_devices)
        if not failed_phones or remaining_devices == 0:
            break

        # 过滤掉已标记失败和正在通话的设备
        available_devices = [
            d
            for d in devices
            if d not in success_dict and d not in failed_devices and get_call_state(d)
        ]
        if not available_devices:
            time.sleep(1)
            continue

        # 准备任务
        tasks = []
        for device in available_devices[: len(failed_phones)]:
            phone = failed_phones.pop(0)
            tasks.append(
                (phone, device, success_dict, failed_phones, failed_devices, lock)
            )

        # 执行任务
        with Pool(processes=len(tasks)) as pool:
            results = pool.map(assign_phone_to_device, tasks)

    # 返回结果
    assignment = dict(success_dict)
    remaining_phones = list(failed_phones)
    manager.shutdown()
    return assignment, remaining_phones


def make_a_call(phoneNumber, deviceid):
    try:
        # 优化点2：更安全的命令执行方式
        res = subprocess.run(
            [
                "adb",
                "-s",
                deviceid,
                "shell",
                "am",
                "start",
                "-a",
                "android.intent.action.CALL",
                "-d",
                f"tel:{phoneNumber}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",  # 显式指定编码
            timeout=10,
        )
        return "Error" not in res.stdout and "error" not in res.stdout
    except:
        return False


def get_call_state(device_id):
    try:
        res = subprocess.run(
            ["adb", "-s", device_id, "shell", "dumpsys", "telephony.registry"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",  # 显式指定编码
            timeout=5,
        )
        if (
            "Error" in res.stdout
            or "error" in res.stdout
            or "Error" in res.stderr
            or "error" in res.stderr
        ):
            return False
        # 检查输出中是否包含通话状态
        if (
            "mCallState=2" in res.stderr
            or "mCallState=4" in res.stderr
            or "mCallState=1" in res.stderr
            or "mCallState=3" in res.stderr
            or "mCallState=2" in res.stdout
            or "mCallState=4" in res.stdout
            or "mCallState=1" in res.stdout
            or "mCallState=3" in res.stdout
        ):
            return False
        else:
            return True
    except:
        return False  # 异常时视为设备忙


# 发送企微机器人通知
async def send_notice(notice_id, type, data):
    try:
        from views.task.task_model import Msg_Notice

        notice = await Msg_Notice.filter(id=notice_id).first().values()
        if type == "app_report":
            report_url = f"{report_ip}/app_report?result_id={data['result_id']}"
            # 自动化--结果通知
            notice["script"]["wechat"]["content"] = (
                notice["script"]["wechat"]["content"]
                .replace("{{result_id}}", str(data["result_id"]))
                .replace("{{device_name}}", str(data["device_name"]))
                .replace("{{percent}}", str(data["percent"]))
                .replace("{{total}}", str(data["total"]))
                .replace("{{passed}}", str(data["passed"]))
                .replace("{{fail}}", str(data["fail"]))
                .replace("{{un_run}}", str(data["un_run"]))
                .replace("{{report_url}}", report_url)
            )
        elif type == "api_report":
            report_url = f"{report_ip}/_api_report?result_id={data['result_id']}"
            notice["script"]["wechat"]["content"] = (
                notice["script"]["wechat"]["content"]
                .replace("{{result_id}}", str(data["result_id"]))
                .replace("{{device_name}}", str(data["device_name"]))
                .replace("{{percent}}", str(data["percent"]))
                .replace("{{total}}", str(data["total"]))
                .replace("{{passed}}", str(data["passed"]))
                .replace("{{fail}}", str(data["fail"]))
                .replace("{{un_run}}", str(data["un_run"]))
                .replace("{{report_url}}", report_url)
            )
        elif type == "app_error_report":
            # APP自动化--异常通知
            report_url = f"{report_ip}/app_result_list"
            notice["script"]["wechat"]["content"] = (
                notice["script"]["wechat"]["content"]
                .replace("{{device_name}}", str(data["device_name"]))
                .replace("{{report_url}}", report_url)
            )
        elif type == "static_check_error":
            # 静态检测--异常通知
            static_check_url = f"{report_ip}/sdk_check"
            notice["script"]["wechat"]["content"] = (
                notice["script"]["wechat"]["content"]
                .replace("{{task_name}}", str(data["task_name"]))
                .replace("{{package}}", str(data["package"]))
                .replace("{{static_check_url}}", static_check_url)
            )
        elif type == "sdk_config_check":
            sdk_config_url = f"{report_ip}/sdk_config_list"
            notice["script"]["wechat"]["content"] = (
                notice["script"]["wechat"]["content"]
                .replace("{{task_name}}", str(data["task_name"]))
                .replace("{{percent}}", str(data["percent"]))
                .replace("{{total}}", str(data["total"]))
                .replace("{{passed}}", str(data["passed"]))
                .replace("{{fail}}", str(data["fail"]))
                .replace("{{sdk_config_url}}", sdk_config_url)
            )
        elif type == "error_notice":
            notice["script"]["wechat"]["content"] = notice["script"]["wechat"][
                "content"
            ].replace("{{error_message}}", str(data["error_message"]))
        else:
            notice["script"]["wechat"]["content"] = data
        if notice["type"] == 1 and notice["status"] == 1:
            await send_wechat_notice(notice)
        elif notice["type"] == 2 and notice["status"] == 1:
            await send_dingding_notice(notice)
        elif notice["type"] == 3 and notice["status"] == 1:
            await send_email_notice(notice)
    except Exception as e:
        print(f"发送通知失败，原因是：{str(e)}")


async def send_wechat_notice(data):
    try:
        webHookUrl = data["value"]
        wechat = data["script"]["wechat"]
        if wechat["msgtype"] == "text":
            json_data = {
                "msgtype": "text",
                "text": {
                    "content": wechat["content"],
                    "mentioned_list": wechat["mentioned_list"],
                },
            }
        elif wechat["msgtype"] == "markdown":
            wechat["content"] = wechat["content"] + "\n"
            for i in wechat["mentioned_list"]:
                wechat["content"] = wechat["content"] + f"<@{i}>"
            json_data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": wechat["content"],
                },
            }
        elif wechat["msgtype"] == "news":
            json_data = {
                "msgtype": "news",
                "news": {
                    "articles": wechat["news"]["articles"],
                    "mentioned_list": wechat["mentioned_list"],
                },
            }
        headers = {"Content-Type": "application/json", "Charset": "UTF-8"}
        requests.post(webHookUrl, headers=headers, json=json_data)
        print("企业微信机器人信息发送成功")
        return True
    except Exception as e:
        print(f"企业微信机器人信息发送失败，原因是：{str(e)}")
        return False, e


async def send_dingding_notice(data):
    pass


async def send_email_notice(data):
    pass

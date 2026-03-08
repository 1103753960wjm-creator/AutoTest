import json
import re
from fastapi import APIRouter, Request
from pydantic.type_adapter import R
import yaml
from common.device import device_info
from common.paginate import db_page_all
from common.request_to_json import body_to_json, json_to_yaml_safe
from common.return_code import catch_Exception, res_fail, res_success
from common.subprocess_common import async_run_subprocess
from config.settings import mitmproxy_yaml_path
from views.app.app_model import App_device
from views.app_mitmproxy.mitmproxy_model import Mitmproxy_api
from views.app_mitmproxy.mitmproxy_process import process_mitmproxy


router = APIRouter(prefix="/api/mitmproxy")


@router.post("/mitmproxy_start")
async def mitmproxy_start(request: Request):
    try:
        body = await body_to_json(request)
        yaml_data = {}
        with open(mitmproxy_yaml_path, "r") as f:
            content = f.read().strip()
            if content:
                print("有数据")
                with open(mitmproxy_yaml_path, "r", encoding="utf-8") as f2:
                    yaml_data = yaml.safe_load(f2) or {}
            else:
                yaml_data = {"device_list": []}

        # 创建设备ID到设备索引的映射，便于快速查找
        device_id_to_index = {}
        for index, device in enumerate(yaml_data["device_list"]):
            device_id = device.get("deviceid")
            if device_id:
                device_id_to_index[device_id] = index

        # 处理请求中的设备列表
        for new_device in body["device_list"]:
            device_id = new_device.get("deviceid")
            if not device_id:
                continue  # 跳过没有deviceid的设备

            # 检查设备是否已存在
            if device_id in device_id_to_index:
                # 更新现有设备（只修改result_id，保留其他字段）
                index = device_id_to_index[device_id]
                yaml_data["device_list"][index]["result_id"] = body["result_id"]
            else:
                # 添加新设备
                device_to_add = new_device.copy()
                device_to_add["result_id"] = body["result_id"]
                yaml_data["device_list"].append(device_to_add)

        # 写入yaml文件
        await json_to_yaml_safe(yaml_data)

        # 检查端口并启动mitmproxy
        port = 8088
        status, message = await process_mitmproxy.port_check(port)
        if status:
            await process_mitmproxy.mitmproxy_start(port)
            await process_mitmproxy.change_agent(body["device_list"], port)
        return await res_success({})
    except Exception as e:
        print(f"mitmproxy_start失败, 错误信息: {e}")
        return await catch_Exception(e)


@router.post("/mitmproxy_single_start")
async def mitmproxy_single_start(request: Request):
    try:
        body = await body_to_json(request)
        yaml_data = {}
        with open(mitmproxy_yaml_path, "r") as f:
            content = f.read().strip()
            if content:
                with open(mitmproxy_yaml_path, "r", encoding="utf-8") as f2:
                    yaml_data = yaml.safe_load(f2) or {}
            else:
                yaml_data = {"device_list": []}
        device_list = {
            "device_list": [
                {
                    "deviceid": body["deviceid"],
                    "result_id": body["result_id"],
                    "wifi_ip": body["wifi_ip"],
                    "id": body["id"],
                }
            ]
        }
        device_found = False
        if not yaml_data["device_list"]:
            await json_to_yaml_safe(device_list)
        else:
            for l in yaml_data["device_list"]:
                if l["deviceid"] == body["deviceid"]:
                    l["result_id"] = body["result_id"]
                    l["wifi_ip"] = body["wifi_ip"]
                    l["id"] = body["id"]
                    device_found = True
            if not device_found:
                add_device = {
                    "deviceid": body["deviceid"],
                    "result_id": body["result_id"],
                    "wifi_ip": body["wifi_ip"],
                    "id": body["id"],
                }
                yaml_data["device_list"].append(add_device)
        await json_to_yaml_safe(yaml_data)
        port = body["port"]
        status, message = await process_mitmproxy.port_check(port)
        print("检查端口", status, message)
        if status:
            process_status, res = await process_mitmproxy.mitmproxy_start(port)
            await process_mitmproxy.change_agent(
                device_list["device_list"],
                port,
            )
            if process_status:
                return await res_success(res)
            else:
                return await catch_Exception(res)
        else:
            await process_mitmproxy.change_agent(device_list["device_list"], port)
            return await res_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/mitmproxy_check")
async def mitmproxy_check(request: Request):
    try:
        body = await body_to_json(request)
        res = await async_run_subprocess(
            f"adb -s {body['deviceid']} shell settings get global http_proxy"
        )
        if ":0" == res:
            return await res_success({"status": "stop"})
        else:
            return await res_success({"status": "running"})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/mitmproxy_stop")
async def mitmproxy_stop(request: Request):
    try:
        body = await body_to_json(request)
        status, message = await process_mitmproxy.mitmproxy_stop(
            body["pid"], body["port"], body["device"]
        )
        if status:
            return await res_success({})
        else:
            return await catch_Exception(message)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/mitmproxy_write_api")
async def mitmproxy_write_api(request: Request):
    body = await body_to_json(request)
    try:
        for i in body["request_list"][::-1]:
            await Mitmproxy_api.create(
                device_id=i["device_id"],
                url=i["url"],
                method=i["method"],
                request_headers=i["request_headers"],
                request_body=i["request_body"],
                status=1 if i["status_code"] == 200 else 0,
                response_headers=i["response_headers"],
                response_body=i["response_body"],
                create_time=i["timestamp"],
                result_id=i["result_id"],
                res_time=round(i["res_time"] * 1000),
            )
        return await res_success({})
    except Exception as e:
        print("write_result异常", json.dumps(body))
        print(f"write_result异常：{str(e)}")
        return await catch_Exception(e)


@router.post("/single_write")
async def single_write(request: Request):
    try:
        body = await body_to_json(request)
        for i in body["request_list"][::-1]:
            await Mitmproxy_api.create(
                device_id=body["device_id"],
                url=i["url"],
                method=i["method"],
                headers=i["headers"],
                body=i["body"],
                status=1 if i["status_code"] == "200" else 0,
                response_headers=i["response_headers"],
                response_body=i["response_body"],
                create_time=i["timestamp"],
            )
        return await res_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/mitmproxy_close_agent")
async def mitmproxy_close_agent(request: Request):
    try:
        body = await body_to_json(request)
        await async_run_subprocess(
            f"adb -s {body['deviceid']} shell settings put global http_proxy :0"
        )
        return await res_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/close_all_agent")
async def close_all_agent(request: Request):
    try:
        device = await device_info()
        print(device)
        for i in device[1]:
            await async_run_subprocess(
                f"adb -s {i['deviceid']} shell settings put global http_proxy :0"
            )
        return await res_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/mitmproxy_run_log")
async def mitmproxy_run_log(request: Request):
    try:
        data = await db_page_all(Mitmproxy_api, request, ["user_id"], order="-id")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

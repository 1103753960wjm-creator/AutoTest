from datetime import datetime
import os
from fastapi import APIRouter, Request
from common.device import (
    device_info,
    app_install,
    get_performance,
    uninstall_app,
    install_app,
)
from common.paginate import db_page_all
from common.request_to_json import body_to_json
from common.return_code import (
    add_success,
    catch_Exception,
    edit_success,
    install_success,
    res_fail,
    res_success,
    uninstall_success,
)
from common.time_str import img_review
from views.app.app_model import App_device, App_device_install, App_device_log
from views.app.device_process import Device_process
from config.settings import device, ip

router = APIRouter(prefix="/api/device")


@router.post("/device_list")
async def device_list():
    try:
        device_list = await App_device.all().values()
        device = await device_info()
        for i in device[1]:
            for j in device_list:
                if i["deviceid"] == j["device_id"]:
                    i["id"] = j["id"]
        return await res_success(device[1])
    except Exception as e:
        return await catch_Exception(e)


@router.post("/device_install")
async def device_install(request: Request):
    try:
        body = await body_to_json(request)
        process = Device_process()
        process.install_process(install_app, body["config"])
        return await install_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/device_uninstall")
async def device_uninstall(request: Request):
    try:
        body = await body_to_json(request)
        process = Device_process()
        process.uninstall_process(uninstall_app, body)
        return await uninstall_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/package_list")
async def package_list(request: Request):
    try:
        data = await body_to_json(request)
        # 文件夹路径
        folder_path = data["folder_path"]
        n = 0
        result = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                n = n + 1
                sdk_dict = {"id": n, "file_name": filename}
                result.append(sdk_dict)
        return await res_success(result)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/device_info_list")
async def device_info_list(request: Request):
    try:
        await App_device.filter(device_status=1).update(
            device_status=3,
        )
        res = await device_info()
        if res[0]:
            for i in res[1]:
                await App_device.filter(
                    device_id=i["deviceid"], device_status=3
                ).update(device_status=1)
            data = await db_page_all(
                App_device, request, key=["user_id"], order="device_status"
            )
            for j in data["content"]:
                for l in res[1]:
                    if j["device_id"] == l["deviceid"]:
                        j["wifi_ip"] = l["wifi_ip"]
            res = await img_review(data["content"])
            data["content"] = res
            return await res_success(data)
        else:
            return await catch_Exception(res[1])
    except Exception as e:
        return await catch_Exception(e)


@router.post("/use_device")
async def use_device(request: Request):
    try:
        data = await body_to_json(request)
        device_status = await App_device.filter(id=data["id"]).first().values()
        if device_status["device_status"] != 1:
            return await res_fail("该设备正在使用中")
        res = {}
        res["device_url"] = (
            f"{device}/#!action=stream&udid={data['device_id']}&player=mse&ws=ws%3A%2F%2F{ip}%3A8000%2F%3Faction%3Dproxy-adb%26remote%3Dtcp%253A8886%26udid%3D{data['device_id']}"
        )
        res["file_url"] = (
            f"{device}/#!action=list-files&udid={data['device_id']}&path=%2Fsdcard"
        )
        await App_device.filter(id=data["id"]).update(device_status=2)
        log = await App_device_log.create(
            user_id=data["user_id"],
            device_id=data["id"],
            end_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        res["log_id"] = log.id
        return await res_success(res)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/app_view_device")
async def app_view_device(request: Request):
    try:
        data = await body_to_json(request)
        res = {}
        res["device_url"] = (
            f"{device}/#!action=stream&udid={data['device_id']}&player=mse&ws=ws%3A%2F%2F{ip}%3A8000%2F%3Faction%3Dproxy-adb%26remote%3Dtcp%253A8886%26udid%3D{data['device_id']}"
        )
        return await res_success(res)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/stop_device")
async def stop_device(request: Request):
    try:
        data = await body_to_json(request)
        await App_device.filter(id=data["id"]).update(device_status=1)
        await App_device_log.filter(id=data["log_id"]).update(
            end_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        return await res_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/get_device_log")
async def get_device_log(request: Request):
    try:
        data = await db_page_all(App_device_log, request, key=["user_id"], order="-id")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/add_device")
async def add_device(request: Request):
    try:
        data = await body_to_json(request)
        await App_device.create(**data)
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/edit_device")
async def edit_device(request: Request):
    try:
        data = await body_to_json(request)
        await App_device.filter(id=data["id"]).update(**data)
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/device_install_app")
async def device_install_app(request: Request):
    try:
        data = await body_to_json(request)
        await App_device_install.create(
            apk_name=data["filename"],
            apk_path=data["file_url"],
            device_id=data["phone_id"],
            user_id=data["user_id"],
        )
        res = await app_install(data)
            
        if res[0]:
            return await res_success({})
        else:
            return await catch_Exception(res[1])
    except Exception as e:
        return await catch_Exception(e)


@router.post("/direct_install_app")
async def direct_install_app(request: Request):
    try:
        data = await body_to_json(request)
        apk = await App_device_install.filter(id=data["id"]).first()
        data["file_url"] = apk.apk_path
        res = await app_install(data)
        if res[0]:
            return await res_success(res[1])
        else:
            return await catch_Exception(res[1])
    except Exception as e:
        return await catch_Exception(e)


@router.post("/get_history_list")
async def get_history_list(request: Request):
    try:
        data = await db_page_all(
            App_device_install, request, key=["user_id"], order="-id"
        )
        for i in data["content"]:
            device = await App_device.filter(id=i["device_id"]).first().values()
            i["device_name"] = device["device_name"]
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/device_performance")
async def device_performance(request: Request):
    try:
        body = await body_to_json(request)
        data = await get_performance(body["device_id"], body["performance"])
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

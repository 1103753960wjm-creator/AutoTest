import json
import os.path
from datetime import datetime, timedelta
from pathlib import Path
import time
from unittest import result
import psutil
from fastapi import APIRouter, status
from fastapi import Request
from tortoise.expressions import Q
from common import device
from common.device import get_performance
from common.paginate import db_page_all
from views.app.app_common import get_img_address, send_app_warn, wait_process_run
from views.app.app_script import airtest_log, run_script
from common.multi_process import Multi_process
from common.request_to_json import body_to_json
from common.return_code import (
    catch_Exception,
    res_success,
    save_success,
    run_success,
    del_success,
    edit_success,
    del_fail,
    stop,
    running,
)
from common.table_tree import create_tree
from common.time_str import time_to_str
from views.app.app_model import (
    App_device,
    App_menu,
    App_script,
    App_result_list,
    App_result,
)
from views.common.upload_model import airtest_img
from views.warning_call.call_commom import send_notice

router = APIRouter(prefix="/api/app")


@router.post("/app_menu")
async def get_menu(request: Request):
    try:
        data = await create_tree(
            model=App_menu, fields=["id", "name", "pid", "type"], search={}
        )
        script = await App_script.all().values()
        type_list = [0, 2, 3, 4, 5]
        # for i in script:
        #     if i["script"] and i["id"] in [24, 29]:
        #         for j in i["script"]:
        #             if j and j["type"] in type_list:
        #                 if j["android"]["img"] is not None:
        #                     print(j["android"]["img"])
        #                     img = (
        #                         await airtest_img.filter(id=j["android"]["img"])
        #                         .first()
        #                         .values()
        #                     )
        #                     print(img)
        #                     j["android"]["img"] = [img["menu_id"], j["android"]["img"]]
        #                 if j["android"]["assert"] is not None:
        #                     img = (
        #                         await airtest_img.filter(id=j["android"]["assert"])
        #                         .first()
        #                         .values()
        #                     )
        #                     j["android"]["assert"] = [
        #                         img["menu_id"],
        #                         j["android"]["assert"],
        #                     ]
        #         await App_script.filter(id=i["id"]).update(script=i["script"])
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/get_app_script")
async def get_app_script(request: Request):
    try:
        body = await body_to_json(request)
        data = await App_script.filter(menu_id=body["id"]).first().values()
        res = await time_to_str(data)
        return await res_success(res)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/save_app_script")
async def save_app_script(request: Request):
    try:
        body = await body_to_json(request)
        await App_script.filter(menu_id=body["id"]).update(
            script=body["script"],
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_id=body["user_id"],
        )
        return await save_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/run_app_script")
async def run_app_script(request: Request):
    try:
        body = await body_to_json(request)
        data = await App_script.get(menu_id=body["id"])
        menu = await App_menu.get(id=body["id"])
        script = await get_img_address(data.script)
        body["script"] = [{"id": body["id"], "script": script}]
        manager = Multi_process()
        result = manager.create_process(run_script, body, len(body["device_list"]))
        now_time = time.time()
        for i in body["device_list"]:
            await App_device.filter(device_id=i["deviceid"]).update(device_status=2)
            for j in result[1]:
                if i["deviceid"] == j["deviceid"]:
                    i["pid"] = j["pid"]
                    i["notice_time"] = time.time() + 3 * 60
        await App_result_list.create(
            task_name=body["task_name"],
            device_list=body["device_list"],
            script_list=[{"id": body["id"], "name": menu.name}],
            script_status=[],
            result_id=body["result_id"],
        )
        # await wait_process_run(result[1])
        return await run_success({"pid_list": result[1]})
        # return await run_success({"pid_list": []})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/run_script_list")
async def run_script_list(request: Request):
    try:
        body = await body_to_json(request)
        body["script"] = []
        script_list = sorted(body["script_list"], key=lambda x: x["step"])
        for i in script_list:
            data = await App_script.get(menu_id=i["id"])
            script = await get_img_address(data.script)
            body["script"].append({"id": i["id"], "script": script})
        manager = Multi_process()
        result = manager.create_process(run_script, body, len(body["device_list"]))
        now_time = time.time()
        for i in body["device_list"]:
            await App_device.filter(device_id=i["deviceid"]).update(device_status=2)
            for j in result[1]:
                if i["deviceid"] == j["deviceid"]:
                    i["pid"] = j["pid"]
                    i["notice_time"] = time.time() + 3 * 60
        await App_result_list.create(
            task_name=body["task_name"],
            device_list=body["device_list"],
            script_list=script_list,
            script_status=[],
            result_id=body["result_id"],
        )
        # await wait_process_run(result[1])
        return await run_success({"pid_list": result[1]})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/add_menu")
async def add_menu(request: Request):
    try:
        body = await body_to_json(request)
        menu = await App_menu.create(
            name=body["name"],
            type=body["type"],
            pid=body["pid"],
            user_id=body["user_id"],
        )
        await App_script.create(script=[], menu_id=menu.id, user_id=body["user_id"])
        return await res_success(
            {
                "name": body["name"],
                "type": body["type"],
                "id": menu.id,
                "pid": body["pid"],
            }
        )
    except Exception as e:
        return await catch_Exception(e)


@router.post("/del_menu")
async def add_menu(request: Request):
    try:
        body = await body_to_json(request)
        if body["type"] == 1:
            if await App_menu.filter(pid=body["id"]).count() > 0:
                return await del_fail({})
        await App_menu.filter(id=body["id"]).delete()
        await App_script.filter(menu_id=body["id"]).delete()
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/rename_menu")
async def add_menu(request: Request):
    try:
        body = await body_to_json(request)
        await App_menu.filter(id=body["id"]).update(name=body["name"])
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/pid_status")
async def pid_status(request: Request):
    try:
        body = await body_to_json(request)
        pid = body["pid"]
        if psutil.pid_exists(pid):
            process = psutil.Process(pid)
            return await running({"message": f"进程状态: {process.status()}"})
        else:
            return await stop({"message": "进程已终止"})
    except Exception as e:
        return await stop({"message": "进程已终止"})


@router.post("/get_process")
async def get_process(request: Request):
    try:
        body = await body_to_json(request)
        for i in body["device_list"]:
            if psutil.pid_exists(i["pid"]):
                process = psutil.Process(i["pid"])
                status = process.status()
                return await res_success({"message": "进程已存在", "status": status})
        return await res_success({"message": "进程已存在", "status": "running"})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/stop_process")
async def stop_process(request: Request):
    body = await body_to_json(request)
    pid = body["pid"]
    result_id = body["result_id"]
    deviceid = body["deviceid"]
    await App_device.filter(device_id=deviceid).update(device_status=3)
    manager = Multi_process()
    manager.stop_process_pid(pid)
    script = await App_result_list.filter(result_id=result_id).first().values()
    total = 0
    result = await App_result.filter(result_id=result_id, device=deviceid).filter(
        ~Q(status=2)
    )
    for i in script["script_list"]:
        app_script = await App_script.filter(menu_id=i["id"]).first().values()
        total = total + len(app_script["script"])
    print("result===========", result)
    res = await App_result.filter(result_id=result_id, device=deviceid).first().values()
    menu_id = res["menu_id"]
    last_performance = res["performance"]
    performance = await get_performance(deviceid, last_performance)
    await airtest_log(
        deviceid,
        result_id,
        1,
        "执行结束",
        menu_id,
        "自动化任务执行完成，请查看执行结果",
        "",
        "",
        performance,
        f"",
        {},
    )
    res = await App_result_list.get(result_id=result_id)
    fail = 0
    passed = 0
    for i in result:
        if i.status == 0:
            fail = fail + 1
        elif i.status == 1:
            passed = passed + 1
    un_run = total - passed - fail
    if total == 0:
        percent = 0
    else:
        percent = round(((total - fail - 1 - un_run) / total) * 100, 2)
    script_res = res.script_status
    script_res.append(
        {
            "device": deviceid,
            "fail": fail,
            "passed": passed,
            "un_run": un_run,
            "total": total,
            "percent": percent,
            "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    await App_result_list.filter(result_id=result_id).update(
        script_status=script_res, end_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    device_info = await App_device.filter(device_id=deviceid).first().values()
    data = {
        "device_name": device_info["device_name"],
        "result_id": result_id,
        "total": total,
        "fail": fail,
        "passed": passed,
        "un_run": total - fail - passed,
        "percent": percent,
    }
    await send_notice(26, "app_report", data)
    return await stop({})


@router.post("/get_app_result")
async def get_app_result(request: Request):
    try:
        body = await body_to_json(request)
        result_id = body["result_id"]
        device = body["device"]
        await send_app_warn(result_id)
        res = (
            await App_result.filter(result_id=result_id, device=device)
            .order_by("-id")
            .values()
        )
        data = await time_to_str(res)
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/get_result_detail")
async def get_result_detail(request: Request):
    global end_time
    script_fail = 0
    script_total = 0
    script_pass = 0
    percent = 0
    try:
        body = await body_to_json(request)
        res = await App_result_list.filter(result_id=body["result_id"]).first().values()
        data = await time_to_str(res)
        start_time = data["start_time"]
        for j in data["script_status"]:
            if j["device"] == body["device"]:
                script_fail = j["fail"]
                script_pass = j["passed"]
                script_total = j["total"]
                script_un_run = j["un_run"]
                percent = j["percent"]
                end_time = j["end_time"]
        return await res_success(
            {
                "script_total": script_total,
                "script_pass": script_pass,
                "script_fail": script_fail,
                "percent": percent,
                "end_time": end_time,
                "start_time": start_time,
                "script_un_run": script_un_run,
            }
        )
    except Exception as e:
        return await catch_Exception(e)


@router.post("/menu_script_list")
async def menu_script_list(request: Request):
    try:
        body = await body_to_json(request)
        script = await App_menu.filter(pid=body["id"])
        res_list = []
        for i in script:
            res = {"id": i.id, "name": i.name, "type": i.type}
            res_list.append(res)
        return await res_success(res_list)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/app_result_list")
async def app_result_list(request: Request):
    try:
        data = await db_page_all(App_result_list, request, key=["user_id"], order="-id")
        for i in data["content"]:
            if i["script_status"]:
                percent = 0
                for j in i["script_status"]:
                    percent = percent + j["percent"]
                i["percent"] = round(percent / len(i["script_status"]), 2)
        return await res_success(data)
    except Exception as e:

        return await catch_Exception(e)


@router.post("/get_result_list")
async def get_result_list(request: Request):
    try:
        body = await body_to_json(request)
        res = (
            await App_result.filter(
                result_id=body["result_id"],
                menu_id=body["menu_id"],
                device=body["device"],
            )
            .order_by("-id")
            .values()
        )
        data = await time_to_str(res)
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/get_app_result_detail")
async def get_app_result_detail(request: Request):
    try:
        body = await body_to_json(request)
        res = await App_result_list.filter(result_id=body["result_id"]).first().values()
        data = await time_to_str(res)
        # 使用字典来快速查找对应关系
        device_dict = {item["device"]: item for item in data["script_status"]}
        for j in data["device_list"]:
            device = j["deviceid"]
            if device in device_dict and device_dict[device]["fail"] > 0:
                j["status"] = 0
            else:
                j["status"] = 1
        percent = 0
        passed = 0
        fail = 0
        total = 0
        un_run = 0
        for j in data["script_status"]:
            percent += j["percent"]
            passed += j["passed"]
            fail += j["fail"]
            total += j["total"]
            un_run += j["un_run"]
        data["percent"] = round(percent / len(data["script_status"]), 2)
        data["passed"] = passed
        data["fail"] = fail
        data["total"] = total
        data["un_run"] = un_run
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/get_script_list")
async def get_script_list(request: Request):
    try:
        body = await body_to_json(request)
        res = await App_menu.filter(type=2).values()
        data = await time_to_str(res)
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/view_script_list")
async def view_script_list(request: Request):
    try:
        body = await body_to_json(request)
        script = await App_script.filter(menu_id=body["menu_id"]).first().values()
        script_list = script["script"]
        return await res_success(script_list)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/app_correction")
async def app_correction(request: Request):
    """
    云真机进行错误修正处理接口
    """
    try:
        body = await body_to_json(request)
        await App_result.filter(
            result_id=body["result_id"], device=body["device"], status=0
        ).update(status=1)
        return await res_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/app_menu_select")
async def app_menu_select(request: Request):
    try:
        res = await App_menu.filter(type=1).values("id", "name")
        return await res_success(res)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/pause_process")
async def pause_process(request: Request):
    try:
        data = await body_to_json(request)
        process = Multi_process()
        process.pause_process(data["pid"])
        return await res_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/resume_process")
async def resume_process(request: Request):
    try:
        data = await body_to_json(request)
        process = Multi_process()
        process.resume_process(data["pid"])
        return await res_success({})
    except Exception as e:
        return await catch_Exception(e)

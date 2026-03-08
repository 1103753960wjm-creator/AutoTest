import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
import time
from config.settings import playwright_result_path
from pathlib import Path
import os
from fastapi import APIRouter, Request
from common.db_curd import db_delete, db_select_all, db_select_id
from common.multi_process import Multi_process
from common.paginate import db_page_all
from common.request_to_json import body_to_json
from common.return_code import (
    add_success,
    catch_Exception,
    del_fail,
    del_success,
    edit_success,
    res_fail,
    res_success,
    stop,
)
from common.table_tree import create_tree
from common.time_str import img_review, time_to_str
from views.web.sync_web_commom import async_run_web
from views.web.web_commom import (
    analysis_element,
    analysis_web_script,
    filter_by_time_range,
    time_add,
)
from views.web.web_model import (
    Web_element,
    Web_group,
    Web_menu,
    Web_result_detail,
    Web_result_list,
    Web_script,
)
from views.web.web_process import Web_process


router = APIRouter(prefix="/api/web")


@router.post("/web_menu")
async def get_menu(request: Request):
    try:
        data = await create_tree(
            model=Web_menu, fields=["id", "name", "pid", "type"], search={}
        )
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/get_web_script")
async def get_app_script(request: Request):
    try:
        body = await body_to_json(request)
        data = await Web_script.filter(menu_id=body["id"]).first().values()
        res = await time_to_str(data)
        return await res_success(res)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/menu_script_list")
async def menu_script_list(request: Request):
    try:
        body = await body_to_json(request)
        script = await Web_menu.filter(pid=body["id"])
        res_list = []
        for i in script:
            res = {"id": i.id, "name": i.name, "type": i.type}
            res_list.append(res)
        return await res_success(res_list)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/add_menu")
async def add_menu(request: Request):
    try:
        body = await body_to_json(request)
        menu = await Web_menu.create(
            name=body["name"],
            type=body["type"],
            pid=body["pid"],
            user_id=body["user_id"],
        )
        if body["type"] == 2:
            await Web_script.create(
                script=[
                    {
                        "name": "打开",
                        "type": 0,
                        "action": {
                            "type": 1,
                            "input": "",
                            "assert": [],
                            "target": "",
                            "element": "",
                            "cookies": [],
                            "localstorage": [],
                            "locator": 1,
                            "up_type": 1,
                            "before_wait": 1,
                            "after_wait": 1,
                            "sway_type": 1,
                            "target_id": "",
                            "wait_time": 1,
                            "element_id": None,
                            "target_type": 1,
                            "locator_select": 1,
                            "target_locator": 1,
                            "target_locator_select": 1,
                        },
                        "status": True,
                        "children": [],
                    }
                ],
                menu_id=menu.id,
                user_id=body["user_id"],
            )
        return await add_success(
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
async def del_menu(request: Request):
    try:
        body = await body_to_json(request)
        if body["type"] == 1:

            if await Web_menu.filter(pid=body["id"]).count() > 0:
                return await del_fail({})
        await Web_menu.filter(id=body["id"]).delete()
        await Web_script.filter(menu_id=body["id"]).delete()
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/rename_menu")
async def rename_menu(request: Request):
    try:
        body = await body_to_json(request)
        await Web_menu.filter(id=body["id"]).update(name=body["name"])
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/save_script")
async def save_script(request: Request):
    try:
        body = await body_to_json(request)
        await Web_script.filter(menu_id=body["id"]).update(
            script=body["script"],
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_id=body["user_id"],
        )
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/input_element")
async def input_element(request: Request):
    try:
        body = await body_to_json(request)
        file_path = f"./{body['file_url']}/{body['file_name']}"
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        result = await analysis_element(
            body["file_name"], body["user_id"], body["pid"], data
        )
        if result[0]:
            return await res_success(result[1])
        else:
            return await catch_Exception(result[1])
    except Exception as e:
        return await catch_Exception(e)


@router.post("/run_web_script")
async def run_web_script(request: Request):
    try:
        if await Web_result_list.filter(status=0).count() > 0:
            return await res_fail("执行失败，当前有执行任务正在队列中，请稍后执行")
        data = await body_to_json(request)
        result = await analysis_web_script(data)
        await Web_result_list.create(
            task_name=data["task_name"],
            user_id=data["user_id"],
            browser_list=data["browser"],
            result=[],
            result_id=data["result_id"],
            script_list=data["script"],
            start_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status=0,
        )
        if result[0]:
            web_process = Web_process()
            await web_process.run_web_process(result[2], result[3])
        return await res_success(result[1])
    except Exception as e:
        return await catch_Exception(e)


@router.post("/stop_web_script")
async def stop_web_script(request: Request):
    try:
        body = await body_to_json(request)
        pid = body["pid"]
        manager = Multi_process()
        manager.stop_process_pid(pid)
        return await stop({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/get_web_result")
async def get_web_result(request: Request):
    try:
        body = await body_to_json(request)
        res = (
            await Web_result_detail.filter(
                result_id=body["result_id"], browser=body["browser"]
            )
            .order_by("-id")
            .values()
        )
        for i in res:
            if i["assert_result"]:
                i["assert_result"] = await img_review(i["assert_result"])
        res_img = await img_review(res)
        data = await time_to_str(res_img)
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/get_web_result_log")
async def get_web_result_log(request: Request):
    try:
        body = await body_to_json(request)
        result_id = body["result_id"]
        browser = body["browser"]
        BASE_APP_DIR = Path(f"{playwright_result_path}/{result_id}/{browser}")
        if not BASE_APP_DIR.exists():
            os.makedirs(BASE_APP_DIR)
        path = BASE_APP_DIR / f"{browser}_result.txt"
        with open(path, "r") as file:
            content = file.read()
        log = content.split("\n")
        log_list = log[::-1]
        return await res_success(log_list[1:])
    except Exception as e:
        return await catch_Exception(e)


@router.post("/get_web_result_list")
async def get_web_result_list(request: Request):
    try:
        data = await db_page_all(Web_result_list, request, key=["user_id"], order="-id")
        for i in data["content"]:
            total = 0
            total_fail = 0
            for j in i["result"]:
                total = total + j["total"]
                total_fail = total_fail + j["run_false"]
            i["percent"] = (
                round((total - total_fail) / total * 100, 2) if total > 0 else 0
            )
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/get_web_result_report")
async def get_web_result_report(request: Request):
    try:
        body = await body_to_json(request)
        result_id = body["result_id"]
        res = await Web_result_list.filter(result_id=result_id).first().values()
        result = await time_to_str(res)
        total = 0
        total_fail = 0
        for i in result["result"]:
            total = total + i["total"]
            total_fail = total_fail + i["run_false"]
        for j in result["script_list"]:
            script_result = await Web_result_detail.filter(
                result_id=result_id, menu=j["id"], status=0
            ).count()
            if script_result > 0:
                j["status"] = 0
            else:
                j["status"] = 1
        result["percent"] = (
            round((total - total_fail) / total * 100, 2) if total > 0 else 0
        )
        result["total"] = total
        result["total_fail"] = total_fail
        return await res_success(result)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/get_web_result_detail")
async def get_web_result_detail(request: Request):
    try:
        body = await body_to_json(request)
        result_id = body["result_id"]
        browser = body["browser"]
        menu_id = body["menu_id"]
        media = (
            await Web_result_detail.filter(
                result_id=result_id, browser=browser, log="执行结束"
            )
            .first()
            .values()
        )
        media = await img_review(media)
        video = media["video"]
        trace = media["trace"]
        res = (
            await Web_result_detail.filter(
                result_id=result_id, browser=browser, menu=menu_id
            )
            .order_by("-id")
            .values()
        )
        img_show = await img_review(res)
        data = await time_to_str(img_show)
        print(data[-1]["create_time"])
        start_time = data[-1]["create_time"]
        end_time = await time_add(data[0]["create_time"])
        print(start_time)
        BASE_APP_DIR = Path(f"{playwright_result_path}/{result_id}/{browser}")
        if not BASE_APP_DIR.exists():
            os.makedirs(BASE_APP_DIR)
        path = BASE_APP_DIR / f"{browser}_result.txt"
        with open(path, "r") as file:
            content = file.read()
        log = content.split("\n")

        log_list = await filter_by_time_range(log, start_time, end_time)
        return await res_success(
            {"content": data, "log": log_list[::-1], "video": video, "trace": trace}
        )
    except Exception as e:
        return await catch_Exception(e)


@router.post("/get_script_list")
async def get_script_list(request: Request):
    try:
        res = await Web_menu.filter(type=2).values()
        data = await time_to_str(res)
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/web_group_list")
async def web_group_list(request: Request):
    try:
        data = await db_page_all(Web_group, request, key=["user_id"], order="-id")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/add_web_group")
async def add_web_group(request: Request):
    try:
        body = await body_to_json(request)
        await Web_group.create(
            name=body["name"],
            script=body["script"],
            description=body["description"],
            user_id=body["user_id"],
        )
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/edit_web_group")
async def edit_web_group(request: Request):
    try:
        body = await body_to_json(request)
        await Web_group.filter(id=body["id"]).update(
            name=body["name"],
            script=body["script"],
            user_id=body["user_id"],
            description=body["description"],
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/del_web_group")
async def del_web_group(request: Request):
    try:
        await db_delete(Web_group, request)
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/web_group_select")
async def web_group_select(request: Request):
    try:
        data = await db_select_all(Web_group)
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/group_add_script")
async def group_add_script(request: Request):
    try:
        body = await body_to_json(request)
        res = []
        for i in body["web_list"]:
            menu = await Web_menu.filter(id=i[-1]).first().values()
            if menu["type"] == 2:
                res.append(menu)
        return await res_success(res)
    except Exception as e:
        return await catch_Exception(e)

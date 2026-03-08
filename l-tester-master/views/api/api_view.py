
from datetime import datetime, timedelta
import json
import time
from fastapi import APIRouter, Request
from common.db_curd import db_delete, db_select_all
from common.paginate import db_page_all
from common.request_to_json import body_to_json
from common.return_code import add_success, catch_Exception, del_success, edit_success, res_success
from common.table_tree import create_tree
from common.time_str import img_review, time_to_str
from views.api.api_common import handle_api_request
from views.api.api_script import handle_api_script
from views.api.common import compare_data, json_body
from views.api.gitlab_commom import handle_gitlab
from views.api.api_model import Api, Api_code, Api_db, Api_edit, Api_envs, Api_menu, Api_project, Api_result, Api_script, Api_script_result, Api_script_result_list, Api_service, Api_var
from views.task.task_common import Apscheduler_task
from views.user.user_model import User_info
from config.settings import api_result_path
from pathlib import Path
import os

router = APIRouter(prefix="/api/api")

@router.post("/api_project")
async def api_project(request: Request):
    try:
        data = await db_page_all(Api_project, request, ["user_id"], "id")
        data["content"] = await img_review(data["content"])
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/api_service")
async def api_service(request: Request):
    try:
        data = await db_page_all(Api_service, request, ["user_id"], "id")
        data["content"] = await img_review(data["content"])
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)
@router.post("/api_tree")
async def api_tree(request: Request):
    try:
        body = await body_to_json(request)
        data = await create_tree(model=Api_menu, fields=["id", "name", "pid", "type", "api_id", "api_service_id"], search=body["search"])
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/add_menu")
async def add_menu(request: Request):
    try:
        body = await body_to_json(request)
        if body["type"] != 1:
            api = await Api.create(
                api_service_id=body["api_service_id"],
                url="/",
                document={},
                req={
                    "params_id": None,
                    "body": {},
                    "after": [],
                    "assert": [],
                    "before": [],
                    "config": {"retry": 0, "req_timeout": 5, "res_timeout": 5},
                    "header": [{"key": "Content-Type","value": "application/json","status": True}],
                    "method": 2,
                    "params": [],
                    "body_type": 2,
                    "file_path": [],
                    "form_data": [],
                    "form_urlencoded": []},
                user_id=body["user_id"]
                )
        await Api_menu.create(
            name=body["name"], pid=body["pid"], type=body["type"],
            api_service_id=body["api_service_id"], status=1, user_id=body["user_id"],
            api_id=api.id if body["type"] != 1 else None
            )
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/edit_menu")
async def edit_menu(request: Request):
    try:
        body = await body_to_json(request)
        await Api_menu.filter(id=body["id"]).update(name=body["name"])
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/del_menu")
async def del_menu(request: Request):
    try:
        body = await body_to_json(request)
        if body["type"] != 1:
            await Api.filter(id=body["api_id"]).delete()
        await db_delete(Api_menu, request)
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/copy_menu")
async def copy_menu(request: Request):
    try:
        body = await body_to_json(request)
        api = await Api.filter(id=body["api_id"]).first().values()
        del api["id"]
        new= await Api.create(**api)
        api_id = new.id
        res = await Api_menu.filter(id=body["id"]).first().values()
        res["api_id"] = api_id
        del res["id"]
        await Api_menu.create(**res)
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)

# 开放接口给api文档平台使用
@router.post("/service_api_update")
async def service_api_update(request: Request):
    try:
        body = await body_to_json(request)
        user = await User_info.filter(account=body["author"]).first().values()
        if body["token"] != "1fefb62cdd834925983f72c2bc9b9c55":
            return await catch_Exception("检验token失败，请联系-管理员")
        for i in body["commonErrorCodes"]:
            if await Api_code.filter(code=i["code"]).exists():
                await Api_code.filter(code=i["code"]).update(code=i["code"], name=i["msg"], user_id=user["id"])
            else:
                await Api_code.create(code=i["code"], name=i["msg"], user_id=user["id"])
        print("gitlab service = ", body["serverName"])
        if await Api_service.filter(name=body["serverName"]).count() <= 0:
            if "overseas" in body["serverName"]:
                project_id = 2
                service = await Api_service.create(
                    name=body["serverName"],
                    img="",
                    user_id=1,
                    api_project_id=project_id
                    )
                service_id = service.id
            else:
                project_id = 1
                service = await Api_service.create(
                    name=body["serverName"],
                    img="",
                    user_id=1,
                    api_project_id=project_id
                    )
                service_id = service.id
        else:
            service = await Api_service.filter(name=body["serverName"]).first().values()
            service_id = service["id"]
            project_id = service["api_project_id"]
        result = await handle_gitlab(body["apis"], service_id, user["id"])
        print(result)
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/api_list")
async def api_list(request: Request):
    try:
        body = await body_to_json(request)
        data = await Api_menu.filter(pid=body["id"]).values()
        res = []
        for i in data:
            if i["type"] == 2:
                api = await Api.filter(id=i["api_id"]).values()
                res.append(api)
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/api_info")
async def api_info(request: Request):
    try:
        body = await body_to_json(request)
        data = await Api.filter(id=body["api_id"]).first().values()
        del data["id"]
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/save_api")
async def save_api(request: Request):
    try:
        body = await body_to_json(request)
        body["req"]["body"] = await json_body(body["req"]["body"])
        api = await Api.filter(id=body["id"]).first().values()
        await Api.filter(id=body["id"]).update(
            url=body["url"],
            req=body["req"],
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_id=body["user_id"]
        )
        edit = await compare_data(api["req"], body["req"])
        if edit:
            await Api_edit.create(
                api_id=body["id"],
                edit=edit,
                user_id=body["user_id"]
            )
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/save_api_case")
async def save_api_case(request: Request):
    try:
        body = await body_to_json(request)
        body["req"]["body"] = await json_body(body["req"]["body"])
        api_menu = await Api_menu.filter(api_id=body["id"]).first().values()
        api = await Api.create(
            url=body["url"],
            req=body["req"],
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_id=body["user_id"],
            api_service_id=body["api_service_id"]
        )
        await Api_menu.create(
            api_id=api.id,
            name=body["name"],
            user_id=body["user_id"],
            type=3,
            pid=api_menu["id"],
            api_service_id=body["api_service_id"],
            status=1
        )
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/api_send")
async def api_send(request: Request):
    try:
        body = await body_to_json(request)
        body["req"]["body"] = await json_body(body["req"]["body"])
        res = await handle_api_request(body)
        return await res_success(res)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/api_env")
async def api_env(request: Request):
    try:
        data = await Api_envs.all().values()
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/env_info")
async def env_info(request: Request):
    try:
        body = await body_to_json(request)
        data = await Api_envs.filter(id=body["id"]).first().values()
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/save_env")
async def save_env(request: Request):
    try:
        body = await body_to_json(request)
        for i in body["env_list"]:
            await Api_envs.filter(id=i["id"]).update(config=i["config"], name=i["name"], variable=i["variable"])
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/add_env")
async def add_env(request: Request):
    try:
        body = await body_to_json(request)
        await Api_envs.create(config=body["config"], name=body["name"], user_id=body["user_id"])
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/del_env")
async def del_env(request: Request):
    try:
        await db_delete(Api_envs, request)
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/api_var_list")
async def api_var_list(request: Request):
    try:
        data = await db_page_all(Api_var, request, [], order="-id")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/add_var")
async def add_var(request: Request):
    try:
        body = await body_to_json(request)
        await Api_var.create(name=body["name"], value=body["value"], user_id=body["user_id"])
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/del_var")
async def del_var(request: Request):
    try:
        await db_delete(Api_var, request)
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/edit_var")
async def edit_var(request: Request):
    try:
        body = await body_to_json(request)
        await Api_var.filter(id=body["id"]).update(name=body["name"], value=body["value"], user_id=body["user_id"], update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/api_tree_list")
async def api_tree_list(request: Request):
    try:
        data = await create_tree(model=Api_menu, fields=["id", "name", "pid", "type", "api_id", "api_service_id"], search={})
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/api_db")
async def api_db(request: Request):
    try:
        data = await db_page_all(Api_db, request, ["user_id"], order="-id")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/api_db_list")
async def api_db_list(request: Request):
    try:
        data = await db_select_all(Api_db)
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/add_api_db")
async def add_api_db(request: Request):
    try:
        body = await body_to_json(request)
        await Api_db.create(
            config=body["config"],
            name=body["name"],
            user_id=body["user_id"]
        )
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/edit_api_db")
async def edit_api_db(request: Request):
    try:
        body = await body_to_json(request)
        await Api_db.filter(id=body["id"]).update(
            config=body["config"],
            name=body["name"],
            user_id=body["user_id"],
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/del_api_db")
async def del_api_db(request: Request):
    try:
        await db_delete(Api_db, request)
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/req_history")
async def req_history(request: Request):
    try:
        data = await db_page_all(Api_result, request, ["user_id"], order="-id")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/edit_history")
async def edit_history(request: Request):
    try:
        body = await body_to_json(request)
        data = await Api_edit.filter(api_id=body["api_id"]).order_by("-id").values()
        data = await time_to_str(data)
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/get_api_case")
async def get_api_case(request: Request):
    try:
        body = await body_to_json(request)
        result = []
        for i in body["script"]:
            menu = await Api_menu.filter(api_id=i[-1], type=3).first().values()
            if menu:
                result.append(menu)
        return await res_success(result)
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/api_script_list")
async def api_script_list(request: Request):
    try:
        data = await db_page_all(Api_script, request, ["user_id"], order="-id")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/add_api_script")
async def add_api_script(request: Request):
    try:
        body = await body_to_json(request)
        await Api_script.create(
            script=body["script"],
            name=body["name"],
            config=body["config"],
            description = body["description"],
            type = body["type"],
            user_id=body["user_id"]
        )
        return await add_success({})
    except Exception as e:
       return await catch_Exception(e)

@router.post("/edit_api_script")
async def edit_api_script(request: Request):
    try:
        body = await body_to_json(request)
        await Api_script.filter(id=body["id"]).update(
            script=body["script"],
            name=body["name"],
            config=body["config"],
            user_id=body["user_id"],
            description = body["description"],
            type = body["type"],
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/del_api_script")
async def del_api_script(request: Request):
    try:
        await db_delete(Api_script, request)
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/api_service_list")
async def api_service_list(request: Request):
    try:
        body = await body_to_json(request)
        data = await Api_service.filter(api_project_id=body["project_id"]).values("id", "name")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/run_api_script")
async def run_api_script(request: Request):
    try:
        body = await body_to_json(request)
        await Api_script_result_list.create(
            script=[],
            result_id=body["result_id"],
            name=body["name"],
            config=body["config"],
            user_id=body["user_id"],
            start_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            end_time=None,
            result={}
        )
        await handle_api_script(body)
        return await res_success({})
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/get_api_script_result")
async def get_api_script_result(request: Request):
    try:
        body = await body_to_json(request)
        data = await Api_script_result.filter(result_id=body["result_id"]).order_by("-id").values()
        data = await time_to_str(data)
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/get_api_script_result_list")
async def get_api_script_result_list(request: Request):
    try:
        data = await db_page_all(Api_script_result_list, request, ["user_id"], order="-id")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/get_api_script_log")
async def get_api_script_log(request: Request):
    try:
        body = await body_to_json(request)
        result_id = body["result_id"]
        BASE_APP_DIR = Path(f"{api_result_path}/{result_id}")
        if not BASE_APP_DIR.exists():
            os.makedirs(BASE_APP_DIR)
        path = BASE_APP_DIR / f"{result_id}.txt"
        with open(path, "r") as file:
            content = file.read()
        log = content.split("\n")
        log_list = log[::-1]
        return await res_success(log_list[1:])
    except Exception as e:
        return await catch_Exception(e)

@router.post("/get_api_script_result_detail")
async def get_api_script_result_detail(request: Request):
    try:
        body = await body_to_json(request)
        data = await Api_script_result_list.filter(result_id=body["result_id"]).first().values()
        data = await time_to_str(data)
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/get_api_script_result_detail_list")
async def get_api_script_result_detail_list(request: Request):
    try:
        body = await body_to_json(request)
        data = await Api_script_result.filter(result_id=body["result_id"], menu_id=body["menu_id"]).order_by("-id").values()
        data = await time_to_str(data)
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/get_api_script_result_report_list")
async def get_api_script_result_report_list(request: Request):
    try:
        body = await body_to_json(request)
        data = await Api_script_result.filter(result_id=body["result_id"], menu_id=body["menu_id"]).order_by("-id").values()
        data = await time_to_str(data)
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/get_api_script_report_log")
async def get_api_script_report_log(request: Request):
    try:
        body = await body_to_json(request)
        result_id = body["result_id"]
        menu_id = body["menu_id"]
        BASE_APP_DIR = Path(f"{api_result_path}/{result_id}")
        if not BASE_APP_DIR.exists():
            os.makedirs(BASE_APP_DIR)
        path = BASE_APP_DIR / f"{menu_id}.txt"
        with open(path, "r") as file:
            content = file.read()
        log = content.split("\n")
        log_list = log[::-1]
        return await res_success(log_list[1:])
    except Exception as e:
        return await catch_Exception(e)

@router.post("/get_api_script_list")
async def get_api_script_list(request: Request):
    try:
        data = await Api_script.all().values("id", "name")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

# 开放接口给Gitlab CI构建
@router.post("/gitlab_ci_notice")
async def gitlab_ci_notice(request: Request):  
    try:
        body = await body_to_json(request)
        api_list = await Api_script.filter(type=body["api_project_id"]).values()
        result_id = int(time.time()) * 1000
        # 获取当前时间
        current_time = datetime.now()
        # 计算30秒后的时间
        time_after_30_seconds = current_time + timedelta(seconds=10)
        # 格式化输出
        formatted_time = time_after_30_seconds.strftime("%Y-%m-%d %H:%M:%S")
        api = {
            "id": result_id,
            "result_id": result_id,
            "name": f"Gitlab CI: {body['api_service']}",
            "type": 3,
            "status": 1,
            "script": {
                "api_script_list": [],
                "env_id": body["env_id"]
            },
            "time": {
                "run_time": formatted_time,
                "type": 1
            },
            "notice": {
                "notice_id": [25],
                "status": 1
            },
            "user_id": 1
        }
        for i in api_list:
            if body["api_project_id"] == 1 and body["api_service"] in i["config"]["cn_service"]:
                api["script"]["api_script_list"].append(i["id"])
        task = Apscheduler_task()
        res = await task.add_scheduler_task(api)
        if res:
            return await res_success(body)
        else:
            return await catch_Exception({})
    except Exception as e:
        return await catch_Exception(e)

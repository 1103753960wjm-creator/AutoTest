from datetime import datetime
import json
from fastapi import APIRouter, Request

from common.db_curd import db_delete
from common.paginate import db_page_all
from common.request_to_json import body_to_json
from common.return_code import (
    add_success,
    catch_Exception,
    del_success,
    edit_success,
    res_success,
)
from views.api.api_model import Api_envs, Api_function
from views.task.task_common import Apscheduler_task
from views.task.task_model import Msg_Notice, Scheduler_Task

router = APIRouter(prefix="/api/task")


@router.post("/task_list")
async def task_list(request: Request):
    try:
        data = await db_page_all(Scheduler_Task, request, key=["user_id"], order="-id")
        for i in data["content"]:
            i["next_time"] = Apscheduler_task().get_schedule_task(i["id"])
        # with open ("F:/project/L-Tester/views/task/lapi_app_api_public_function_20250317141348.json", "r", encoding="utf-8") as f:
        #     content = f.read()
        # print(content)
        # for i in json.loads(content)["lapi_app_api_public_function"]:
        #     await Api_function.create(
        #         name=i["name"],
        #         description=i["description"],
        #         user_id=int(i["user_id"]),
        #     )
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/add_task")
async def add_task(request: Request):
    try:
        data = await body_to_json(request)
        schedule = await Scheduler_Task.create(
            name=data["name"],
            script=data["script"],
            status=data["status"],
            time=data["time"],
            type=data["type"],
            description=data["description"],
            notice=data["notice"],
            user_id=data["user_id"],
        )
        if data["status"] == 1:
            data["id"] = schedule.id
            task = Apscheduler_task()
            res = await task.add_scheduler_task(data)
        else:
            return await add_success({})
        if res:
            return await add_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/del_task")
async def del_task(request: Request):
    try:
        await db_delete(Scheduler_Task, request)
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/edit_task")
async def edit_task(request: Request):
    try:
        data = await body_to_json(request)
        await Scheduler_Task.filter(id=data["id"]).update(
            name=data["name"],
            script=data["script"],
            status=data["status"],
            time=data["time"],
            type=data["type"],
            user_id=data["user_id"],
            description=data["description"],
            notice=data["notice"],
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        task = Apscheduler_task()
        if data["status"] == 1:
            res = await task.add_scheduler_task(data)
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/notice_list")
async def notice_list(request: Request):
    try:
        data = await db_page_all(Msg_Notice, request, key=["user_id"], order="-id")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/add_notice")
async def add_notice(request: Request):
    try:
        data = await body_to_json(request)
        await Msg_Notice.create(
            name=data["name"],
            script=data["script"],
            value=data["value"],
            status=data["status"],
            type=data["type"],
            user_id=data["user_id"],
            description=data["description"],
        )
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/del_notice")
async def del_notice(request: Request):
    try:
        await db_delete(Msg_Notice, request)
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/edit_notice")
async def edit_notice(request: Request):
    try:
        data = await body_to_json(request)
        await Msg_Notice.filter(id=data["id"]).update(
            name=data["name"],
            script=data["script"],
            status=data["status"],
            value=data["value"],
            type=data["type"],
            user_id=data["user_id"],
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            description=data["description"],
        )
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/notice_select")
async def notice_select(request: Request):
    try:
        res = []
        data = await Msg_Notice.all().values()
        for i in data:
            res.append({"id": i["id"], "name": i["name"]})
        return await res_success(res)
    except Exception as e:
        return await catch_Exception(e)

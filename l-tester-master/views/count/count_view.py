from datetime import datetime, timedelta
from fastapi import APIRouter, Request
from common.return_code import catch_Exception, res_success
from views.api.api_model import Api_menu, Api_script_result
from views.app.app_model import App_menu, App_result, App_script
from views.count.count_common import get_count_all, run_count
from views.task.task_model import Scheduler_Task
from views.web.web_model import Web_result_detail, Web_menu, Web_script

router = APIRouter(prefix="/api/count")


@router.post("/get_count")
async def get_count(request: Request):
    try:
        result = [
            {
                "value1": 0,
                "title1": "接口总数：",
                "unit": "个",
                "title2": "用例步骤总数：",
                "value2": 0,
            },
            {
                "value1": 0,
                "title1": "Web UI脚本总数：",
                "unit": "个",
                "title2": "用例步骤总数：",
                "value2": 0,
            },
            {
                "value1": 0,
                "title1": "APP脚本总数：",
                "unit": "个",
                "title2": "用例步骤总数：",
                "value2": 0,
            },
            {
                "value1": 0,
                "title1": "定时任务总数：",
                "unit": "个",
                "title2": "已启动任务总数：",
                "value2": 0,
            },
        ]
        result[0]["value1"] = await Api_menu.filter(type=2).count()
        result[0]["value2"] = await Api_menu.filter(type=3).count()

        result[1]["value1"] = await Web_menu.filter(type=2).count()
        result[1]["value2"] = await get_count_all(Web_script)

        result[2]["value1"] = await App_menu.filter(type=2).count()
        result[2]["value2"] = await get_count_all(App_script)

        result[3]["value1"] = await Scheduler_Task.all().count()
        result[3]["value2"] = await Scheduler_Task.filter(status=1).count()
        return await res_success(result)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/get_run_count")
async def get_count(request: Request):
    try:
        result = {
            "api_data": [],
            "web_data": [],
            "app_data": [],
        }
        end_date = datetime.now()
        start_date = end_date - timedelta(days=6)  # 包括今天共7天
        # 1. 生成7天所有日期的列表
        date_range = [
            (start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)
        ]
        result["api_data"] = await run_count(Api_script_result, date_range)
        result["web_data"] = await run_count(Web_result_detail, date_range)
        result["app_data"] = await run_count(App_result, date_range)
        result["date"] = date_range
        return await res_success(result)
    except Exception as e:
        return await catch_Exception(e)

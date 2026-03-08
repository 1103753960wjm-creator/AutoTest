import asyncio
import json
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta, timezone
from common.multi_process import Multi_process
from views.api.api_model import Api_script, Api_script_result_list
from views.api.api_script import handle_api_script
from views.app.app_common import get_img_address
from views.app.app_model import App_menu, App_result_list, App_script
from views.app.app_script import run_script
from views.warning_call.call_commom import send_notice
from views.web.web_commom import analysis_web_script
from views.web.web_model import Web_group, Web_result_list
from views.web.web_process import Web_process

async_scheduler = AsyncIOScheduler()


class Apscheduler_task:
    def __init__(self):
        self.scheduler = async_scheduler

    async def add_scheduler_task(self, data):
        try:
            self.scheduler_time = data["time"]
            if data["type"] == 1:
                app_data = await self.handle_app_data(data)
                app_data["id"] = data["id"]
                await self.create_app_task(app_data)
            elif data["type"] == 2:
                web_data = await self.handle_web_data(data)
                web_data["user_id"] = data["user_id"]
                web_data["id"] = data["id"]
                status, msg, script_list, browser_type = await analysis_web_script(
                    web_data
                )
                if status:
                    await self.create_web_task(web_data, script_list, browser_type)
            elif data["type"] == 3:
                api_data = await self.handle_api_data(data)
                api_data["id"] = data["id"]
                await self.create_api_task(api_data)
            return True
        except Exception as e:
            print(f"add_scheduler_task执行异常失败，原因是：{str(e)}")

    async def handle_app_data(self, data):
        try:
            script = {}
            script["task_name"] = data["name"]
            script["result_id"] = int(time.time()) * 1000
            script["device_list"] = data["script"]["device_list"]
            script["script_list"] = []
            script["script"] = []
            script["user_id"] = data["user_id"]
            for i in data["script"]["app_script_list"]:
                menu = await App_menu.filter(id=i).first().values()
                script["script_list"].append(menu)
                app = await App_script.get(menu_id=i).first().values()
                app_script = await get_img_address(app["script"])
                script["script"].append({"id": i, "script": app_script})
            return script
        except Exception as e:
            print(f"处理app数据失败，原因是：{str(e)}")

    async def create_app_task(self, data):
        try:
            if self.scheduler_time["type"] == 1:
                self.scheduler.add_job(
                    self.app_start,
                    trigger=DateTrigger(run_date=self.scheduler_time["run_time"]),
                    id=str(data["id"]),
                    args=[data],
                )
            elif self.scheduler_time["type"] == 2:
                self.scheduler.add_job(
                    self.app_start,
                    trigger=IntervalTrigger(
                        seconds=self.scheduler_time["interval"] * 60
                    ),
                    id=str(data["id"]),
                    args=[data],
                )
            elif self.scheduler_time["type"] == 3:
                start_time = self.scheduler_time["week_run_time"].split(":")
                self.scheduler.add_job(
                    self.app_start,
                    trigger=CronTrigger(
                        hour=start_time[0], minute=start_time[1]
                    ),  # 每天12:00执行,
                    id=str(data["id"]),
                    args=[data],
                )
            elif self.scheduler_time["type"] == 4:
                start_time = self.scheduler_time["week_run_time"].split(":")
                values = [item for item in self.scheduler_time["week_date"]]
                week_data = ",".join(values)
                self.scheduler.add_job(
                    self.app_start,
                    trigger=CronTrigger(
                        day_of_week=week_data, hour=start_time[0], minute=start_time[1]
                    ),  # 每天12:00执行,
                    id=str(data["id"]),
                    args=[data],
                )
            self.scheduler_start()
            return True, "定时任务创建成功"
        except Exception as e:
            return False, f"定时任务创建失败，原因：{str(e)}"

    async def app_start(self, data):
        try:
            await App_result_list.create(
                task_name=data["task_name"],
                device_list=data["device_list"],
                script_list=data["script_list"],
                script_status=[],
                user_id=data["user_id"],
                result_id=data["result_id"],
            )
            manager = Multi_process()
            manager.create_process(run_script, data, len(data["device_list"]))
        except Exception as e:
            print(f"app_start执行异常失败，原因是：{str(e)}")

    async def handle_web_data(self, data):
        try:
            script = {}
            script["result_id"] = int(time.time()) * 1000
            script["browser_type"] = 2
            script["task_name"] = data["name"]
            script["browser"] = data["script"]["browser"]
            script["width"] = data["script"]["width"]
            script["height"] = data["script"]["height"]
            script["script"] = []
            for i in data["script"]["web_script_list"]:
                menu = await Web_group.filter(id=i).first().values()
                script["script"].extend(menu["script"])
            return script
        except Exception as e:
            print(f"处理web数据失败，原因是：{str(e)}")

    async def create_web_task(self, data, script_list, browser_type):
        try:
            if self.scheduler_time["type"] == 1:
                self.scheduler.add_job(
                    func=self.web_start,
                    trigger=DateTrigger(run_date=self.scheduler_time["run_time"]),
                    id=str(data["id"]),
                    args=[data, script_list, browser_type],
                )
            elif self.scheduler_time["type"] == 2:
                self.scheduler.add_job(
                    self.web_start,
                    trigger=IntervalTrigger(
                        seconds=self.scheduler_time["interval"] * 60
                    ),
                    id=str(data["id"]),
                    args=[data, script_list, browser_type],
                )
            elif self.scheduler_time["type"] == 3:
                start_time = self.scheduler_time["week_run_time"].split(":")
                self.scheduler.add_job(
                    self.web_start,
                    trigger=CronTrigger(
                        hour=start_time[0], minute=start_time[1]
                    ),  # 每天12:00执行,
                    id=str(data["id"]),
                    args=[data, script_list, browser_type],
                )
            elif self.scheduler_time["type"] == 4:
                start_time = self.scheduler_time["week_run_time"].split(":")
                values = [item for item in self.scheduler_time["week_date"]]
                week_data = ",".join(values)
                self.scheduler.add_job(
                    self.web_start,
                    trigger=CronTrigger(
                        day_of_week=week_data, hour=start_time[0], minute=start_time[1]
                    ),  # 每天12:00执行,
                    id=str(data["id"]),
                    args=[data, script_list, browser_type],
                )
            self.scheduler_start()
            self.get_schedule_task(data["id"])
            return True, "定时任务创建成功"
        except Exception as e:
            print(f"create_web_task执行异常失败，原因是：{str(e)}")
            return False, f"定时任务创建失败，原因：{str(e)}"

    async def web_start(self, data, script_list, browser_type):
        try:
            await Web_result_list.create(
                task_name=data["task_name"],
                user_id=data["user_id"],
                browser_list=data["browser"],
                result=[],
                result_id=data["result_id"],
                script_list=data["script"],
                start_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            web_process = Web_process()
            await web_process.run_web_process(script_list, browser_type)
        except Exception as e:
            print(f"web_start执行失败，原因是：{str(e)}")

    async def handle_api_data(self, data):
        try:
            script = {}
            script["result_id"] = int(time.time()) * 1000
            script["name"] = data["name"]
            script["user_id"] = data["user_id"]
            script["config"] = {}
            script["config"]["env_id"] = data["script"]["env_id"]
            script["run_list"] = []
            for i in data["script"]["api_script_list"]:
                menu = (
                    await Api_script.filter(id=i)
                    .first()
                    .values("id", "name", "config", "script")
                )
                script["run_list"].append(menu)
            return script
        except Exception as e:
            print(f"handle_api_data执行异常失败，原因是：{str(e)}")

    async def create_api_task(self, data):
        try:
            if self.scheduler_time["type"] == 1:
                self.scheduler.add_job(
                    self.api_start,
                    trigger=DateTrigger(run_date=self.scheduler_time["run_time"]),
                    id=str(data["id"]),
                    args=[data],
                )
            elif self.scheduler_time["type"] == 2:
                self.scheduler.add_job(
                    self.api_start,
                    trigger=IntervalTrigger(
                        seconds=self.scheduler_time["interval"] * 60
                    ),
                    id=str(data["id"]),
                    args=[data],
                )
            elif self.scheduler_time["type"] == 3:
                start_time = self.scheduler_time["week_run_time"].split(":")
                self.scheduler.add_job(
                    self.api_start,
                    trigger=CronTrigger(
                        hour=start_time[0], minute=start_time[1]
                    ),  # 每天12:00执行,
                    id=str(data["id"]),
                    args=[data],
                )
            elif self.scheduler_time["type"] == 4:
                start_time = self.scheduler_time["week_run_time"].split(":")
                values = [item for item in self.scheduler_time["week_date"]]
                week_data = ",".join(values)
                self.scheduler.add_job(
                    self.api_start,
                    trigger=CronTrigger(
                        day_of_week=week_data, hour=start_time[0], minute=start_time[1]
                    ),  # 每天12:00执行,
                    id=str(data["id"]),
                    args=[data],
                )
            self.scheduler_start()
            return True, "定时任务创建成功"
        except Exception as e:
            print(f"create_api_task执行异常失败，原因是：{str(e)}")
            return False, f"定时任务创建失败，原因：{str(e)}"

    async def api_start(self, data):
        await Api_script_result_list.create(
            name=data["name"],
            user_id=data["user_id"],
            config=data["config"],
            result={},
            result_id=data["result_id"],
            script=[],
            start_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            end_time=None,
        )
        await handle_api_script(data)

    def scheduler_start(self):
        try:
            self.scheduler.start()
            return True, "定时任务开启成功"
        except Exception as e:
            return False, f"定时任务开启失败，原因：{str(e)}"

    def scheduler_resume(self):
        try:
            self.scheduler.resume()
            return True, "定时任务恢复成功"
        except Exception as e:
            return False, f"定时任务恢复失败，原因：{str(e)}"

    def get_schedule_list(self):
        try:
            job_list = self.scheduler.get_jobs()
            return job_list
        except Exception as e:
            print(e)

    def get_schedule_task(self, id):
        try:
            job = self.scheduler.get_job(job_id=str(id))
            if job:
                utc_time = datetime.fromisoformat(str(job[0].next_run_time))
                beijing_time = utc_time.astimezone(timezone(timedelta(hours=8)))
                return beijing_time.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return ""
        except Exception as e:
            print(f"get_schedule_task执行异常失败，原因是：{str(e)}")
            return ""

    def del_schedule_task(self, id):
        try:
            res = self.scheduler.remove_job(str(id))
            if res:
                return True
            return True
        except Exception as e:
            print(e)

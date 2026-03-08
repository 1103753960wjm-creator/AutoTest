from datetime import datetime
import token
from fastapi import FastAPI, HTTPException, Request
from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.staticfiles import StaticFiles
from middleware.token_auth import Token_Auth
from config.settings import ip, port
from db_settings import TORTOISE_ORM
from middleware.log_middleware import Logger_Middleware
from views.app.app_model import App_menu
from views.route import include_router
from tortoise.contrib.fastapi import register_tortoise
from views.task.task_common import Apscheduler_task
from views.task.task_model import Scheduler_Task
from contextlib import asynccontextmanager
from views.api.api_model import Api_envs, Api_menu, Api_project, Api_service
from views.user.user_model import Role, Role_user, User_info
from views.web.web_model import Web_menu, Web_element_menu


@asynccontextmanager
async def startup(app: FastAPI):
    # 重启服务的时候，判断是否有定时任务，如果有则重启
    task = await Scheduler_Task.all().values()
    scheduler = Apscheduler_task()
    for i in task:
        if i["status"] == 1:
            await scheduler.add_scheduler_task(i)
    print(f"{datetime.now()}：定时任务已重启")

    # 待修改：首次启动时，将会创建超管，admin用户，为app自动化，api自动化，web自动化创建根目录（后面可以删掉）
    users = await User_info.all()
    if not users:
        await User_info.create(
            username="admin",
            account="admin",
            password="e10adc3949ba59abbe56e057f20f883e",
            token="xxx",
            token_time="2021-01-01 00:00:00",
            email="xxx",
            phone="12345678912",
            status=1,
            avatar=""
        )
        await Role.create(
            name="超级管理员",
            role_id=1,
            user_id=1
        )
        await Role_user.create(role_id=1, user_id=1)

    api_project = await Api_project.all()
    if not api_project:
        await Api_project.create(name="默认项目", user_id=1, img="xxx")
        await Api_service.create(
            name="默认服务", img="xxx", user_id=1, api_project_id=1
        )
        await Api_menu.create(
            name="默认菜单", type=0, user_id=1, api_service_id=1, status=1, pid=0
        )
        await Api_envs.create(
            name="默认环境",
            user_id=1,
            config=[{"name": "默认环境变量", "value": "默认环境变量"}],
            variable=[{"name": "默认环境变量", "value": "默认环境变量"}],
        )
    app_menu = await App_menu.all()
    if not app_menu:
        await App_menu.create(name="默认菜单", type=0, user_id=1, pid=0)
    web_menu = await Web_menu.all()
    if not web_menu:
        await Web_menu.create(name="默认菜单", type=0, user_id=1, pid=0)
    web_element = await Web_element_menu.all()
    if not web_element:
        await Web_element_menu.create(name="默认菜单", type=0, user_id=1, pid=0)

    yield


# 实例化FastAPI对象，重置定时任务
app = FastAPI(lifespan=startup)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库连接
register_tortoise(
    app,
    config=TORTOISE_ORM,
    # generate_schemas=True,  # 如果数据库为空，则自动生成对应表单，生产环境不要开
    # add_exception_handlers=True,  # 生产环境建议不要开，会泄露调试信息
)

# 挂载路由
include_router(app)

# token校验中间件
app.add_middleware(Token_Auth)

# 注册日志中间件
app.add_middleware(Logger_Middleware)

# 数据压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 静态文件挂载
app.mount("/media", StaticFiles(directory="media"), name="media")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app, host=ip, port=port, workers=1)

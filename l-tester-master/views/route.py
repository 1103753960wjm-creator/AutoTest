from fastapi import FastAPI
from views.ai import ai_view
from views.api import api_view, public_view
from views.app import app_view, img_view, device_view
from views.app_mitmproxy import mitmproxy_view
from views.common import upload_view
from views.exe_update import exe_update_view
from views.requirement import requirement_view
from views.task import task_view
from views.testcase import testcase_view
from views.user import user_view
from views.web import element_view, web_view
from views.count import count_view
from views.warning_call import call_view


def include_router(app: FastAPI):
    """挂载路由.

    Args:
        app (FastAPI): APP.
    """
    # 统计
    app.include_router(count_view.router)
    app.include_router(ai_view.router)
    app.include_router(requirement_view.router)
    app.include_router(testcase_view.router)

    # 用户中心
    app.include_router(user_view.router)

    # 文件上传
    app.include_router(upload_view.router)

    # 接口自动化
    app.include_router(api_view.router)

    # 接口自动化通用函数
    app.include_router(public_view.router)

    # app自动化
    app.include_router(app_view.router)

    # 图片管理
    app.include_router(img_view.router)

    # 设备管理
    app.include_router(device_view.router)

    # web ui自动化
    app.include_router(web_view.router)

    # web ui自动化 元素管理
    app.include_router(element_view.router)

    # 定时任务
    app.include_router(task_view.router)

    # 运维通话告警
    app.include_router(call_view.router)

    # 前端打包更新接口
    app.include_router(exe_update_view.router)

    # mitmproxy接口
    app.include_router(mitmproxy_view.router)

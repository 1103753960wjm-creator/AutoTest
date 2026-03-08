import json
import multiprocessing
import os
import signal
from multiprocessing import Queue
from pathlib import Path
import asyncio
import threading
from common.db_curd import init_db
from views.web.web_commom import run_web_async


class Web_process:

    def __init__(self):
        self.processes = []
        self.pid_list = []
        self.browser_type = None

    async def run_web_process(self, arg, browser_type):
        try:
            self.browser_type = browser_type
            for i in arg:
                await self._run_in_process(i)
        except Exception as e:
            print(f"进程启动失败: {str(e)}")

    async def _run_in_process(self, data):
        try:
            # 子进程初始化异步事件循环和数据库
            await self._async_entry(data)
        except Exception as e:
            print(f"子进程错误: {str(e)}")

    async def _async_entry(self, data):
        # 子进程内初始化数据库
        await init_db()
        # 执行任务
        await run_web_async(data, self.browser_type)

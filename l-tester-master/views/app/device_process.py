import json
import multiprocessing
import os
import signal
from multiprocessing import Queue
from pathlib import Path


class Device_process:

    def __init__(self):
        self.processes = []
        self.pid_list = []
        self.result = []

    def install_process(self, method, arg):
        try:
            # 建立进程池
            for i in arg:
                path = i["path"]
                for j in i["config"]:
                    data = {
                        "path": path,
                        "deviceid": j["deviceid"],
                        "package": j["package"]
                    }
                    p = multiprocessing.Process(target=method, args=(data,))
                    p.start()
        except Exception as e:
            print(f"创建多进程失败， 原因是：{str(e)}")
    def uninstall_process(self, method, arg):
        try:
            package = arg["package"]
            for i in arg["device_list"]:
                data = {
                    "deviceid": i,
                    "package": package
                }
                p = multiprocessing.Process(target=method, args=(data,))
                p.start()
        except Exception as e:
            print(f"创建多进程失败， 原因是：{str(e)}")

    def wait_process(self, processes):
        # 等待进程执行完成
        for j in processes:
            j.join()

    def stop_all_process(self):
        try:
            for l in self.processes:
                l.terminate()
            print('所有进程已停止')
        except Exception as e:
            print(f"进程停止异常，原因：{e}")

    def stop_process_pid(self, pid):
        try:
            os.kill(pid, signal.SIGTERM)  # 发送SIGTERM信号到指定PID的进程
            return True
        except ProcessLookupError as e:
            return False, f"停止进程失败，原因是：{e}"
import json
import multiprocessing
import os
import signal
from multiprocessing import Queue
from pathlib import Path


class Multi_process:

    def __init__(self):
        self.processes = []
        self.pid_list = []
        self.result = []

    def create_process(self, method, arg, processes):
        try:
            # 建立进程池
            for i in range(0, processes):
                print("执行次数:", i)
                p = multiprocessing.Process(
                    target=method,
                    args=(
                        arg["device_list"][i]["deviceid"],
                        arg["script"],
                        arg["result_id"],
                        arg["device_list"][i]["os_type"],
                        arg["run_type"],
                        arg["version"],
                        arg["channel_id"],
                        arg["device_list"][i]["package"],
                        arg["device_list"][i]["path"],
                    ),
                )
                p.start()
                self.processes.append(p)
                self.pid_list.append(
                    {"deviceid": arg["device_list"][i]["deviceid"], "pid": p.pid}
                )
            return self.processes, self.pid_list
        except Exception as e:
            print(f"创建多进程失败， 原因是：{str(e)}")

    def pause_process(self, pid):
        print(f"暂停进程00000-{pid}-")
        # 暂停进程
        for j in self.processes:
            print(f"进程111111-{j.pid}-")
            if pid == j.pid:
                print(f"暂停进程-{j.pid}-")
                j.pause()

    def resume_process(self, pid):
        print(f"恢复进程0000-{pid}-")
        # 恢复进程
        for j in self.processes:
            print(f"进程2222222-{j.pid}-")
            if pid == j.pid:
                print(f"恢复进程-{j.pid}-")
                j.resume()

    def wait_process(self, processes):
        # 等待进程执行完成
        for j in processes:
            j.join()

    def stop_all_process(self):
        try:
            for l in self.processes:
                l.terminate()
            print("所有进程已停止")
        except Exception as e:
            print(f"进程停止异常，原因：{e}")

    def stop_process_pid(self, pid):
        try:
            os.kill(pid, signal.SIGTERM)  # 发送SIGTERM信号到指定PID的进程
            print(f"进程-{pid}-已停止")
            return True
        except ProcessLookupError as e:
            return False, f"停止进程失败，原因是：{e}"

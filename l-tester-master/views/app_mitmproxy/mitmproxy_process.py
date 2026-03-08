import multiprocessing

from common.subprocess_common import async_run_subprocess, sync_run_subprocess
from config.settings import ip, mitmproxy_config_path


class Process_mitmproxy:
    """
    mitmproxy进程管理类，用于使用多进程处理mitmproxy的启动和停止操作。
    """

    def __init__(self):
        """ """
        self.port_list = []
        self.process_list = {}

    async def port_check(self, port):
        """
        端口检查方法
        """
        if port in self.port_list:
            return False, f"端口{port}已被占用, 请重新选择其他端口"
        else:
            self.port_list.append(port)
            return True, "端口可用"

    async def mitmproxy_start(self, port):
        """
        mitmproxy启动方法
        """
        try:
            # 待修改：ip:port 修改本地域名加服务端口
            cmd = f"mitmweb -p {str(port)} --set block_global=false -s {mitmproxy_config_path} --web-host ip:port"
            print(cmd)
            process = multiprocessing.Process(target=sync_run_subprocess, args=(cmd,))
            process.start()
            return True, {
                "port": port,
                "status": "running",
                "message": "mitmproxy启动成功",
                "pid": process.pid,
            }
        except Exception as e:
            print(f"mitmproxy启动失败，原因：{e}")
            return False, {}

    async def change_agent(self, device_list, port):
        """
        修改代理
        """
        try:
            print(f"change_agent启动中1，：{device_list}")
            for i in device_list:
                await async_run_subprocess(
                    f"adb -s {i['deviceid']} shell settings put global http_proxy {ip}:{port}"
                )
            return True
        except Exception as e:
            print(f"change_agent启动失败，原因：{e}")
            return False

    async def mitmproxy_stop(self, pid, port, device_list):
        """
        mitmproxy停止方法
        """
        try:
            print(f"mitmproxy停止中1，：{self.process_list}")
            process = self.process_list[port]
            process.terminate()
            process.join()
            if process.is_alive():  # 判断进程是否存活
                sync_run_subprocess(f"taskkill /F /PID {pid}")
            self.port_list.remove(port)
            self.process_list.pop(port)
            for device in device_list:
                sync_run_subprocess(
                    f"adb -s {device['deviceid']} shell settings put global http_proxy :0"
                )
            return True, "mitmproxy停止成功"
        except Exception as e:
            print(f"mitmproxy停止失败，原因：{e}")
            return False, f"mitmproxy停止失败，原因：{e}"


# 创建Process_mitmproxy对象
process_mitmproxy = Process_mitmproxy()

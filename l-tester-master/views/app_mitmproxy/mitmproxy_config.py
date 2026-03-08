# mitmproxy_save_to_db.py
import base64
from datetime import datetime
import json
import requests
from queue import Queue
import time
from typing import Dict, Any, final
import yaml
from mitmproxy import http


class DatabaseSaver:
    """
    mitmproxy 数据保存到数据库
    通过 HTTP API 转发到 FastAPI 服务
    """

    def __init__(self, api_url):
        self.config = {}
        import threading

        with open(
            "F:/project/L-Tester/views/app_mitmproxy/mitmproxy_config_file.yaml",
            "r",
            encoding="utf-8",
        ) as f:
            self.config = yaml.safe_load(f)  # 使用yaml.safe_load读取YAML文件
        self.device_list = self.config["device_list"]
        self.api_url = api_url

        # 统计信息
        self.stats = {
            "total_received": 0,
            "total_sent": 0,
            "failed_requests": 0,
            "last_error": None,
        }

    def save_request(self, flow: http.HTTPFlow):
        try:
            # 清洗数据
            # 待修改：xxx-对应检查得接口域名
            host = [
                "xxx"
            ]
            if flow.request.host_header in host:
                cleaned_data = self._clean_flow_data(flow)
                self._send_single(cleaned_data, self.api_url)

        except Exception as e:
            print(f"[Error] 处理请求失败: {e}")

    def _clean_flow_data(self, flow: http.HTTPFlow) -> Dict[str, Any]:
        """清洗mitmproxy数据"""
        # 这里有问题，晚点看看
        request_header = dict(flow.request.headers)
        client_ip = flow.client_conn.peername[0] if flow.client_conn.peername else None
        device_id = None
        result_id = None
        for i in self.device_list:
            if i["wifi_ip"] == client_ip:
                device_id = i["id"]
                result_id = i["result_id"]
        data = {
            "device_id": device_id,
            "result_id": result_id,
            "url": flow.request.url,
            "method": flow.request.method,
            "status_code": flow.response.status_code if flow.response else None,
            "request_headers": request_header,
            "response_headers": dict(flow.response.headers) if flow.response else {},
            "request_body": flow.request.content,
            "response_body": flow.response.content,
            "client_ip": (
                flow.client_conn.peername[0] if flow.client_conn.peername else None
            ),
            "res_time": (
                flow.response.timestamp_end - flow.request.timestamp_start
                if flow.response
                else None
            ),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        return data

    def _send_single(self, data: Dict[str, Any], api_url):
        """发送单条数据（队列满时使用）"""
        try:
            json_data = {
                "request_list": [data],
                "batch_size": 1,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            response = requests.post(
                api_url,
                json=json_data,
                timeout=5,
            )

            if response.status_code == 200:
                self.stats["total_sent"] += 1
                print(f"[Success] 发送单条数据成功")
            else:
                self.stats["failed_requests"] += 1

        except Exception as e:
            self.stats["failed_requests"] += 1
            self.stats["last_error"] = str(e)

    def stop(self):
        """停止服务"""
        self.running = False
        if self.sender_thread.is_alive():
            self.sender_thread.join(timeout=5)
        print("[DatabaseSaver] 已停止")


# mitmproxy addon
saver = None


def server_start():
    """mitmproxy启动时调用"""

    global saver
    # 从配置文件或环境变量获取API地址
    # 待修改：ip:port 修改本地域名加服务端口
    api_url = f"http://ip:port/api/mitmproxy/single_write"
    saver = DatabaseSaver(api_url=api_url)


def done():
    """mitmproxy停止时调用"""
    global saver
    if saver:
        saver.stop()


def response(flow: http.HTTPFlow):
    """处理响应"""
    server_start()
    global saver
    if saver:
        saver.save_request(flow)

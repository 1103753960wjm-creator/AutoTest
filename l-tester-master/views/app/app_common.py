# 作者：小林
import asyncio
import subprocess
import threading
from pathlib import Path
from airtest.core.api import *
from airtest.core.cv import Template
from click.core import F
import numpy as np
import cv2
from common.multi_process import Multi_process
from config.settings import project_path, source_ip
from views.app.app_model import App_result, App_result_list
from views.common.upload_model import airtest_img
from views.warning_call.call_commom import send_notice
from PIL import Image


# 等待自动化进程执行
async def wait_process_run(process):
    # 利用多线程，不需要等待进程执行完成
    manager = Multi_process()
    manager.wait_process(process)


async def get_img_address(data):
    try:
        for i in data:
            if (
                i["type"] == 0
                or i["type"] == 2
                or i["type"] == 3
                or i["type"] == 4
                or i["type"] == 5
            ):
                android = i["android"]["img"]
                ios = i["ios"]["img"]
                assert_android = i["android"]["assert"]
                assert_ios = i["ios"]["assert"]
                if android is not None:
                    img = await airtest_img.filter(id=android[-1]).first().values()
                    i["android"]["img"] = f".{img['file_path']}"
                if ios is not None:
                    img = await airtest_img.filter(id=android[-1]).first().values()
                    i["ios"]["img"] = f".{img['file_path']}"
                if assert_android is not None:
                    img = (
                        await airtest_img.filter(id=assert_android[-1]).first().values()
                    )
                    i["android"]["assert"] = f".{img['file_path']}"
                if assert_ios is not None:
                    img = await airtest_img.filter(id=assert_ios[-1]).first().values()
                    i["ios"]["assert"] = f".{img['file_path']}"
        return data
    except Exception as e:
        print(e)


def wait_until_exists(device, target, timeout, interval=1):
    """
    :param target: 目标图片
    :param timeout: 遍历超时时间
    :param interval: 轮询间隔
    :return: 如果在超时时间内存在则返回True，否则返回False
    """
    start_time = time.time()
    while True:
        if exists(Template(f"{target}")):
            return True
        time_out = time.time() - start_time
        if time_out > 20:
            close_target(f"{project_path}/media/app_img/allow_confirm.png")
            close_target(f"{project_path}/media/app_img/vivo_s19_allow_app.png")
            close_target(f"{project_path}/media/app_img/vivo_s19_allow_use.png")
            close_target(f"{project_path}/media/app_img/android_确定.png")
            close_target(f"{project_path}/media/app_img/android_初始同意隐私协议.png")
            close_target(f"{project_path}/media/app_img/android_关闭公告按钮.png")
        if time_out > timeout:
            return False


def wait_until_install(device, timeout, interval=3):
    # 处理安装需要确定
    """
    :param target: 目标图片
    :param timeout: 遍历超时时间
    :param interval: 轮询间隔
    :return: 如果在超时时间内存在则返回True，否则返回False
    """
    res = False
    res = close_target(f"{project_path}/media/app_img/vivos19_check.png")
    res = close_target(f"{project_path}/media/app_img/vivos19_install.png")
    return res



def assert_img_exists(target):
    if assert_exists(Template(f"{target}")):
        return True
    else:
        return False


def close_target(target):
    if exists(Template(f"{target}")):
        touch(Template(f"{target}"))
        return True
    else:
        return False


def wait_until_download(target, timeout, interval=3):
    """
    :param target: 目标图片
    :param timeout: 遍历超时时间
    :param interval: 轮询间隔
    :return: 如果在超时时间内存在则返回True，否则返回False
    """
    try:
        start_time = time.time()
        while True:
            if exists(Template(f"{target}", threshold=0.7)):
                print("Target found.")
                return True
            time_out = time.time() - start_time
            if int(time_out) > timeout:
                print("Exceeded timeout.")
                return False
            sleep(interval)
    except Exception as e:
        print(f"Error in wait_until_download: {e}")
        return False


async def airtest_snapshot(driver, deviceid, result_id):
    try:
        # 设置基础上传目录
        BASE_IMG_DIR = Path(f"media/app_result/{result_id}/{deviceid}")
        BASE_IMG_DIR.mkdir(parents=True, exist_ok=True)
        # 获取保存截图的路径
        filename = "{}.png".format(str(int(time.time())))
        # 拼接文件完整路径
        filepath = os.path.join(BASE_IMG_DIR, filename)
        # 在本地保存截图文件
        driver.snapshot(filepath)
        # 判断是否黑屏
        # await is_black_screen_from_file(deviceid, f"{project_path}/{filepath}")
        return f"{source_ip}/{filepath}"  # 考虑怎么存储
    except Exception as e:
        return str(e)


async def is_black_screen_from_file(deviceid, image_path, threshold=15):
    """
    基于本地图片文件判断是否黑屏
    :param image_path: 图片文件路径
    :param threshold: 亮度阈值(0-255)
    :param debug: 是否显示调试信息
    :return: (是否黑屏, 平均亮度值, 图片尺寸)
    """
    from views.app.app_model import App_device

    try:
        # 读取图片文件
        if not os.path.exists(image_path):
            print(f"❌ 文件不存在: {image_path}")
            return False

        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            print(f"❌ 无法读取图片文件: {image_path}")
            return False

        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape

        # 计算平均亮度
        mean_brightness = np.mean(gray)

        is_black = mean_brightness < threshold

        device = await App_device.filter(device_id=deviceid).values("device_name")
        device_name = device_name[0]["device_name"]

        if is_black:
            content = f"""
                图片检测报告\n\n
                ❗ 设备：{device_name}\n
                📊 图片名称：{Path(image_path).name}\n
                检测结果：{'🚨 检测到黑屏' if mean_brightness < threshold else '✅ 屏幕正常'}"""
            await send_notice(36, 1, content)

        return is_black

    except Exception as e:
        print(f"❌ 处理图片时出错: {e}")
        return False


async def send_app_warn(result_id):
    res = await App_result_list.get(result_id=result_id).values()
    device_list = res["device_list"]
    data = {}
    for i in device_list:
        result = await App_result.filter(
            result_id=result_id, device=i["deviceid"], status=0
        ).count()
        if result > 0:
            now_time = time.time()
            if i["notify"] < 10 and now_time > i["notice_time"]:
                i["notify"] = i["notify"] + 1
                data["device_name"] = i["name"]
                await send_notice(27, "app_error_report", data)
                i["notice_time"] = time.time() + 3 * 60
                await App_result_list.filter(result_id=result_id).update(
                    device_list=device_list
                )


def allocate_package(device_id, version, channel_id):
    try:
        if channel_id == "1000":
            folder_path = (
                f"\\\\Share\\upload\\包体共享\\国服{version}正式包\\android\\官包"
            )
        elif channel_id in ["1006", "1007", "1008", "1019", "1020"]:
            folder_path = (
                f"\\\\Share\\upload\\包体共享\\国服{version}正式包\\android\\cps"
            )
        else:
            folder_path = (
                f"\\\\Share\\upload\\包体共享\\国服{version}正式包\\android\\广告"
            )
        for filename in os.listdir(folder_path):
            if os.path.isfile(file_path) and channel_id in filename:
                file_path = os.path.join(folder_path, filename)
                allocate_install_app(device_id, file_path)
        return True
    except Exception as e:
        return False


def allocate_install_app(device_id, path):
    result = False  # 默认设为False

    try:
        print(f"开始安装设备：{device_id}, 路径：{path}")
        command = f"adb -s {device_id} install -r {path}"
        res = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            timeout=6000,
        )

        full_output = res.stdout + res.stderr
        print(f"安装输出: {full_output}")

        if "Success" in full_output:
            print(f"设备 {device_id} 安装成功")
            result = True  # 只有成功时才改为True
        else:
            print(f"设备 {device_id} 安装失败")
            result = False

    except subprocess.TimeoutExpired as e:
        print(f"设备 {device_id} 安装超时: {e}")
        result = False

    except Exception as e:
        print(f"设备 {device_id} 安装发生错误: {e}")
        result = False

    finally:
        # 最终一定会返回result，且result一定有值
        return result


# 检查设备是否安装app
def check_app_install(device_id):
    try:
        # 待修改：包名
        command = f"adb -s {device_id} shell pm path 包名"
        res = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3000,
            encoding="utf-8",
        )
        # 待修改：包名
        if (
            "待修改：包名" in res.stdout
            or "待修改：包名" in res.stderr
        ):
            return True
        else:
            return False
    except Exception as e:
        print(f"函数check_app_install()，异常:{e}")
        return False

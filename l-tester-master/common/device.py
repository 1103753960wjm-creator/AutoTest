# 作者：小林
import json
import os
import re
import subprocess
from sys import stdout
import time
from datetime import datetime
import psutil
from common.subprocess_common import async_run_subprocess
from views.app.app_model import App_device
from views.app.device_process import Device_process


async def device_info():
    try:
        cmd = "tidevice list --json"
        device_info_list = []
        ios_result = os.popen(cmd).read().replace("\\n", "").replace("\u001b[0m", "")
        if eval(ios_result):
            for i in eval(ios_result):
                if i["market_name"] == "-":
                    name = i["name"]
                else:
                    name = i["market_name"]
                ios = {
                    "deviceid": i["udid"],
                    "name": name,
                    "os_type": "ios",
                    "version": i["product_version"],
                }
                device_info_list.append(ios)
        else:
            device_info_list = []
        devices_output = await async_run_subprocess("adb devices")
        if devices_output != "List of devices attached":
            devices_list = devices_output.split("\n")[1:]
            for device in devices_list:
                device_id = device.split("\t")[0]
                app_device = (
                    await App_device.filter(device_id=device.split("\t")[0])
                    .first()
                    .values()
                )
                output = await async_run_subprocess(f"adb -s {device_id} shell getprop")
                device_info_output = output
                brand = await get_property(device_info_output, "ro.product.brand")
                if brand == "OPPO":
                    if (
                        await get_property(device_info_output, "ro.oppo.market.name")
                        == ""
                    ):
                        device_name = await get_property(
                            device_info_output, "ro.vendor.oplus.market.name"
                        )
                    else:
                        device_name = await get_property(
                            device_info_output, "ro.oppo.market.name"
                        )
                    version = str(
                        await get_property(
                            device_info_output, "ro.product.build.version.release"
                        )
                    )
                elif brand == "HUAWEI":
                    # 鸿蒙系统
                    version = "Harmony OS " + str(
                        await get_property(
                            device_info_output, "hw_sc.build.platform.version"
                        )
                    )
                    device_name = await get_property(
                        device_info_output, "ro.config.marketing_name"
                    )
                elif brand == "Redmi":
                    device_name = await get_property(
                        device_info_output, "ro.product.marketname"
                    )
                    version = str(
                        await get_property(
                            device_info_output, "ro.product.build.version.release"
                        )
                    )
                elif brand == "SG":
                    device_name = await get_property(device_info_output, "ro.sh.brand")
                    version = str(
                        await get_property(
                            device_info_output, "ro.system.build.version.release"
                        )
                    )
                elif brand == "XIAOMI":
                    device_name = await get_property(
                        device_info_output, "ro.product.model"
                    )
                    version = str(
                        await get_property(
                            device_info_output, "ro.product.build.version.release"
                        )
                    )
                elif brand == "OnePlus":
                    device_name = await get_property(
                        device_info_output, "ro.product.device"
                    )
                    version = str(
                        await get_property(
                            device_info_output, "ro.product.build.version.release"
                        )
                    )
                elif brand == "google":
                    device_name = await get_property(
                        device_info_output, "ro.product.model"
                    )
                    version = str(
                        await get_property(
                            device_info_output, "ro.product.build.version.release"
                        )
                    )
                elif brand == "HONOR":
                    device_name = await get_property(
                        device_info_output, "ro.config.marketing_name"
                    )
                    version = str(
                        await get_property(
                            device_info_output, "ro.product.build.version.release"
                        )
                    )
                elif brand == "samsung":
                    device_name = await get_property(
                        device_info_output, "ro.product.model"
                    )
                    version = str(
                        await get_property(
                            device_info_output, "ro.product.build.version.release"
                        )
                    )
                elif brand == "vivo":
                    device_name = await get_property(device_info_output, "net.hostname")
                    version = str(
                        await get_property(
                            device_info_output, "ro.build.version.release"
                        )
                    )
                else:
                    device_name = await get_property(
                        device_info_output, "ro.product.brand"
                    )
                    version = "未知操作系统版本"
                if app_device:
                    device_name = app_device["device_name"]
                device_id = await get_property(device_info_output, "ro.serialno")
                wifi_ip = await get_wifi_ip(device_id)
                device_info_list.append(
                    {
                        "deviceid": device_id,
                        "name": device_name,
                        "os_type": "android",
                        "version": version,
                        "wifi_ip": wifi_ip,
                    }
                )
            else:
                return True, device_info_list
        return True, device_info_list
    except Exception as e:
        print(f"获取设备信息失败: {e}")
        return False, str(e)


async def get_property(device_info_output, type_name):
    for line in device_info_output.split("\n"):
        if line.startswith(f"[{type_name}]"):
            return line.split(":")[-1][2:-1]
    return ""


async def get_performance(device_id, device_performance):
    try:
        memory = await get_memory(device_id)
        cpu = await get_cpu(device_id)
        temperature = await get_temperature(device_id)
        network = await get_network(device_id)
        now_time = await get_now()
        device_performance["time"].append(now_time)
        device_performance["memory"].append(memory)
        device_performance["cpu"].append(cpu)
        device_performance["temperature"].append(temperature)
        device_performance["up_network"].append(network[0])
        device_performance["down_network"].append(network[1])
        return device_performance
    except Exception as e:
        device_performance["time"].append(await get_now())
        device_performance["memory"].append(0)
        device_performance["cpu"].append(0)
        device_performance["temperature"].append(0)
        device_performance["up_network"].append(0)
        device_performance["down_network"].append(0)
        return device_performance


async def get_now():
    now = datetime.now()
    minute = now.minute
    second = now.second
    return str(minute) + ":" + str(second)

# 内存
async def get_memory(device_id):
    cmd = "adb -s {} shell cat /proc/meminfo".format(device_id)
    result = os.popen(cmd).read().split()
    memory = (int(result[1]) - int(result[7])) / int(result[1]) * 100
    return round(memory, 2)


# CPU
async def get_cpu_info(device_id):
    cmd = "adb -s {} shell cat /proc/stat".format(device_id)
    result = os.popen(cmd).read().split()
    return result


# CPU
async def get_cpu(device_id):
    # 获取第一个时间点的CPU信息
    stat1 = await get_cpu_info(device_id)
    # 等待一段时间
    time.sleep(0.1)
    # 获取第二个时间点的CPU信息
    stat2 = await get_cpu_info(device_id)
    # 计算总的CPU时间
    total1 = sum([int(stat1[i]) for i in range(1, 8)])
    total2 = sum([int(stat2[i]) for i in range(1, 8)])
    # 计算空闲的CPU时间
    idle1 = int(stat1[4])
    idle2 = int(stat2[4])
    total = total2 - total1
    idle = idle2 - idle1
    # 计算CPU使用率
    cpu_usage = (total - idle) / total * 100
    return round(cpu_usage, 2)


# 实时网速
async def get_network(device_id):
    try:
        # 获取第一次网络统计数据
        cmd = f"adb -s {device_id} shell cat /proc/net/dev"
        output1 = subprocess.check_output(cmd, shell=True).decode().strip()
        rx1 = tx1 = 0
        for line in output1.splitlines():
            if ":" in line and "lo:" not in line:  # 排除本地回环接口
                fields = line.split(":")[1].strip().split()
                rx1 += int(fields[0])  # 接收的字节数
                tx1 += int(fields[8])  # 发送的字节数

        # 等待1秒
        time.sleep(1)

        # 获取第二次网络统计数据
        output2 = subprocess.check_output(cmd, shell=True).decode().strip()
        rx2 = tx2 = 0
        for line in output2.splitlines():
            if ":" in line and "lo:" not in line:
                fields = line.split(":")[1].strip().split()
                rx2 += int(fields[0])
                tx2 += int(fields[8])

        # 计算速度（转换为 Kb/s）
        download_speed = (rx2 - rx1) * 8 / 1024 / 1024  # bytes -> kilobits
        upload_speed = (tx2 - tx1) * 8 / 1024  # bytes -> kilobits

        return round(upload_speed, 2), round(download_speed, 2)
    except Exception as e:
        print(f"获取网速失败: {str(e)}")
        return 0, 0


# 磁盘（代替使用，具体待重写）
async def get_disk():
    disk_io = psutil.disk_io_counters()
    return (
        int(disk_io.read_count),
        int(disk_io.write_count),
        int(disk_io.read_bytes),
        int(disk_io.write_bytes),
    )


# 手机温度
async def get_temperature(device_id):
    command = f"adb -s {device_id} shell dumpsys battery"
    output = subprocess.check_output(command, shell=True).decode("utf-8")
    temperature_line = next(
        line for line in output.splitlines() if "temperature" in line
    )
    temperature_value = int(temperature_line.split(":")[1].strip()) / 10
    return temperature_value


# 获取手机短信
def get_sms(now_time, device_id, timeout=3000000, interval=1):
    sms_code = "000000"
    while sms_code == "000000":
        cmd = f"adb -s {device_id} shell content query --uri content://sms/"
        data = subprocess.check_output(cmd).decode("utf-8")
        list_1 = data.split("Row: ")
        # 使用等号分割文本
        key_value_pairs = list_1[1].split(", ")
        my_dict = {}
        for pair in key_value_pairs:
            if "body" in pair or "date" in pair:
                key, value = pair.split("=")
                my_dict[key] = value
        # 待修改：识别文案
        if int(my_dict["date"]) > now_time and "识别文案" in my_dict["body"]:
            code = re.search(r"\d+", my_dict["body"])
            sms_code = code.group(0)
            return sms_code
        if time.time() * 1000 - now_time > timeout:
            return sms_code
        time.sleep(interval)


def install_app(data):
    try:
        path = data["path"]
        device_id = data["deviceid"]
        package = data["package"]
        cmd = f"adb -s {device_id} install -r {path}\\{package}"
        subprocess.check_output(cmd, shell=True)
        return True
    except Exception as e:
        return False, str(e)


def uninstall_app(data):
    try:
        device_id = data["deviceid"]
        package = data["package"]
        cmd = f"adb -s {device_id} uninstall {package}"
        subprocess.check_output(cmd, shell=True)
        return True
    except Exception as e:
        return False, str(e)


async def app_install(data):
    try:
        path = data["file_url"]
        device_id = data["device_id"]
        package = data["filename"]
        cmd = f"adb -s {device_id} install -r .{path}/{package}"
        subprocess.check_output(cmd, shell=True)
        return True, "安装成功"
    except Exception as e:
        return False, str(e)


# 获取手机连接的wifi地址
async def get_wifi_ip(device_id):
    """获取WiFi IP地址的多种方法"""

    try:
        methods = [
            # 方法1: ip命令
            ("ip addr show wlan0", r"inet (\d+\.\d+\.\d+\.\d+)/"),
            # 方法2: ifconfig
            ("ifconfig wlan0", r"inet addr:(\d+\.\d+\.\d+\.\d+)"),
            # 方法3: netcfg
            ("netcfg", r"wlan0\s+[^\s]+\s+[^\s]+\s+(\d+\.\d+\.\d+\.\d+)/"),
            # 方法4: dumpsys wifi
            ("dumpsys wifi", r"ipAddress=(\d+\.\d+\.\d+\.\d+)"),
        ]

        for cmd, pattern in methods:
            result = subprocess.run(
                ["adb", "-s", device_id, "shell", cmd],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.stdout.strip():
                match = re.search(pattern, result.stdout.strip())
                if match:
                    return match.group(1)
        return None
    except Exception as e:
        return None

# 作者：小林
import asyncio
from datetime import datetime
from pathlib import Path
from airtest.core.api import *
from airtest.core.cv import Template
from numpy import number
from tortoise import Tortoise
from config.settings import project_path, source_ip
from db_settings import (
    Mysql_Database,
    Mysql_Host,
    Mysql_Port,
    Mysql_password,
    Mysql_username,
)
from views.app.app_common import (
    allocate_install_app,
    allocate_package,
    check_app_install,    
    wait_until_download,
    wait_until_exists,
    airtest_snapshot,
    assert_img_exists,
    wait_until_install,
)
from common.device import get_performance, get_sms
from views.app.app_model import App_device, App_result, App_result_list
from views.warning_call.call_commom import send_notice


# 初始化数据库连接
async def init_db():
    await Tortoise.init(
        db_url=f"mysql://{Mysql_username}:{Mysql_password}@{Mysql_Host}:{Mysql_Port}/{Mysql_Database}",
        modules={
            "models": [
                "aerich.models",
                "views.user.user_model",
                "views.common.upload_model",
                "views.app.app_model",
                "views.task.task_model",
            ]
        },
    )
    await Tortoise.generate_schemas()


async def airtest_log(
    deviceid,
    result_id,
    status,
    name,
    menu_id,
    res_log,
    before_img,
    after_img,
    performance,
    video,
    assert_value,
):
    from views.app.app_model import App_result
    from datetime import datetime

    await App_result.create(
        result_id=result_id,
        name=name,
        log=res_log,
        status=status,
        before_img=before_img,
        after_img=after_img,
        menu_id=menu_id,
        performance=performance,
        video=video,
        assert_value=assert_value,
        device=deviceid,
        create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


async def task_end(result_id, deviceid, total, end_time):
    global script_res
    from views.app.app_model import App_result, App_result_list, App_device
    from tortoise.expressions import Q

    result = await App_result.filter(
        ~Q(status=2), result_id=result_id, device=deviceid
    ).values("status")
    script_res = await App_result_list.filter(result_id=result_id).values(
        "script_status"
    )
    await App_device.filter(device_id=deviceid).update(device_status=3)
    fail = 0
    passed = 0
    for i in result:
        if i["status"] != 0:
            passed = passed + 1
        else:
            fail = fail + 1
    un_run = total - passed - fail
    if total == 0:
        percent = 0
    else:
        percent = round(((total - fail - un_run) / total) * 100, 2)
    script_res[0]["script_status"].append(
        {
            "device": deviceid,
            "fail": fail,
            "passed": passed,
            "un_run": un_run,
            "total": total,
            "percent": percent,
            "end_time": end_time,
        }
    )
    await App_result_list.filter(result_id=result_id).update(
        script_status=script_res[0]["script_status"], end_time=end_time
    )
    device_name = await App_device.filter(device_id=deviceid).values("device_name")
    data = {
        "device_name": device_name[0]["device_name"],
        "result_id": result_id,
        "total": total,
        "fail": fail,
        "passed": passed,
        "un_run": un_run,
        "percent": percent,
    }
    await send_notice(26, "app_report", data)


def run_script(
    device: str,
    data: list,
    result_id: str,
    os_type: str,
    run_type: int,
    version: str,
    channel_id: str,
    package: str,
    path: str,
):
    global menu_id
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_db())
    BASE_IMG_DIR = Path(f"media/app_result/{result_id}/{device}")
    BASE_IMG_DIR.mkdir(parents=True, exist_ok=True)
    video = os.path.join(BASE_IMG_DIR, f"{result_id}.mp4")
    print(f"视频保存路径：{video}")
    if os_type == "android":
        driver = connect_device(
            f"Android:///{device}?cap_method=javacap&touch_method=adb"
        )
    else:
        driver = init_device(platform="IOS", uuid=f"http+usbmux://{device}")
    performance = {
        "time": [],
        "memory": [],
        "cpu": [],
        "temperature": [],
        "up_network": [],
        "down_network": [],
    }
    driver.start_recording(
        max_time=36000,
        fps=60,
        bitrate=2592000,
        mode="ffmpeg",
        max_size=5000000,
        output=video,
        snapshot_sleep=0.1,
    )
    total = 0
    if run_type == 1:
        file_path = f"{path}\\{package}"
        performance = asyncio.run(get_performance(device, performance))
        loop.run_until_complete(
            airtest_log(
                device,
                result_id,
                2,
                "设备包体分配",
                data[0]["id"],
                f"开始分配设备，包体：{package}",
                "",
                "",
                performance,
                "",
                {},
            )
        )
        res = allocate_install_app(device, file_path)
        performance = asyncio.run(get_performance(device, performance))
        loop.run_until_complete(
            airtest_log(
                device,
                result_id,
                2,
                "安装包体",
                data[0]["id"],
                f"正在安装包体：{package}",
                "",
                "",
                performance,
                "",
                {},
            )
        )
        if not res:
            performance = asyncio.run(get_performance(device, performance))
            loop.run_until_complete(
                airtest_log(
                    device,
                    result_id,
                    2,
                    "处理安装权限",
                    data[0]["id"],
                    f"正在处理安装权限...",
                    "",
                    "",
                    performance,
                    "",
                    {},
                )
            )
            check_status = check_app_install(device)
            while not check_status:
                until = wait_until_install(device, 300)
                if until:
                    check_status = True
        performance = asyncio.run(get_performance(device, performance))
        loop.run_until_complete(
            airtest_log(
                device,
                result_id,
                2,
                "安装成功",
                data[0]["id"],
                f"{package}：安装成功",
                "",
                "",
                performance,
                "",
                {},
            )
        )

    else:
        res = allocate_package(device, version, channel_id)
        if not res:
            check_status = check_app_install(device)
            while not check_status:
                until = wait_until_install(device, 300)
                if until:
                    check_status = True
    for i in data:
        menu_id = i["id"]
        total = total + len(i["script"])
        for j in i["script"]:
            before_img = asyncio.run(airtest_snapshot(driver, device, result_id))
            if j["status"]:
                time.sleep(1)
                if j["type"] == 0:
                    after_img = asyncio.run(airtest_snapshot(driver, device, result_id))
                    performance = asyncio.run(get_performance(device, performance))
                    res_log = f"等待热更..."
                    # res_log = f"模拟长时间等待..."
                    loop.run_until_complete(
                        airtest_log(
                            device,
                            result_id,
                            1,
                            j["name"],
                            menu_id,
                            res_log,
                            before_img,
                            after_img,
                            performance,
                            "",
                            {},
                        )
                    )
                    # 目的主要是长时间等待更新完成
                    if wait_until_download(target=j["android"]["img"], timeout=18000):
                        pass
                elif j["type"] == 1:
                    try:
                        sleep(5)
                        start_app(j["package"])
                        after_img = asyncio.run(
                            airtest_snapshot(driver, device, result_id)
                        )
                        performance = asyncio.run(get_performance(device, performance))
                        res_log = f"启动APP：{j['package']}, 成功"
                        loop.run_until_complete(
                            airtest_log(
                                device,
                                result_id,
                                1,
                                j["name"],
                                menu_id,
                                res_log,
                                before_img,
                                after_img,
                                performance,
                                "",
                                {},
                            )
                        )
                    except Exception as e:
                        res_log = f"启动APP：{j['package']}, 失败，原因是：{str(e)}"
                        after_img = asyncio.run(
                            airtest_snapshot(driver, device, result_id)
                        )
                        performance = asyncio.run(get_performance(device, performance))
                        loop.run_until_complete(
                            airtest_log(
                                device,
                                result_id,
                                0,
                                j["name"],
                                menu_id,
                                res_log,
                                before_img,
                                after_img,
                                performance,
                                "",
                                {},
                            )
                        )
                elif j["type"] == 2:
                    try:
                        res = "点击成功"
                        now_time = time.time()
                        if j["name"] == "检查热更version，并进入游戏":
                            path = f"{project_path}" + before_img.replace(source_ip, "")
                            ocr_data = ocr_version(path)
                            res = f"版本号：{ocr_data}，点击进入游戏成功"
                        if wait_until_exists(device, j["android"]["img"], timeout=180):
                            target = Template(j["android"]["img"])
                            touch(target)
                            res_log = res
                            performance = asyncio.run(
                                get_performance(device, performance)
                            )
                            if j["android"]["assert"] is not None:
                                if assert_img_exists(j["android"]["assert"]):
                                    if j["name"] == "支付成功，点击返回游戏":
                                        time.sleep(3)
                                    after_img = asyncio.run(
                                        airtest_snapshot(driver, device, result_id)
                                    )
                                    assert_value = {
                                        "img": after_img,
                                        "result": "断言通过",
                                    }
                                    loop.run_until_complete(
                                        airtest_log(
                                            device,
                                            result_id,
                                            1,
                                            j["name"],
                                            menu_id,
                                            res_log,
                                            before_img,
                                            after_img,
                                            performance,
                                            "",
                                            assert_value,
                                        )
                                    )
                                else:
                                    after_img = asyncio.run(
                                        airtest_snapshot(driver, device, result_id)
                                    )
                                    assert_value = {
                                        "img": after_img,
                                        "result": "断言失败",
                                    }
                                    loop.run_until_complete(
                                        airtest_log(
                                            result_id,
                                            0,
                                            j["name"],
                                            menu_id,
                                            res_log,
                                            before_img,
                                            after_img,
                                            performance,
                                            "",
                                            assert_value,
                                        )
                                    )
                            else:
                                after_img = asyncio.run(
                                    airtest_snapshot(driver, device, result_id)
                                )
                                loop.run_until_complete(
                                    airtest_log(
                                        device,
                                        result_id,
                                        1,
                                        j["name"],
                                        menu_id,
                                        res_log,
                                        before_img,
                                        after_img,
                                        performance,
                                        "",
                                        {},
                                    )
                                )
                        else:
                            res_log = f'{j["android"]["img"]}，图像识别失败'
                            after_img = asyncio.run(
                                airtest_snapshot(driver, device, result_id)
                            )
                            performance = asyncio.run(
                                get_performance(device, performance)
                            )
                            loop.run_until_complete(
                                airtest_log(
                                    device,
                                    result_id,
                                    0,
                                    j["name"],
                                    menu_id,
                                    res_log,
                                    before_img,
                                    after_img,
                                    performance,
                                    "",
                                    {},
                                )
                            )
                    except Exception as e:
                        res_log = f"点击失败，原因是：{str(e)}"
                        after_img = asyncio.run(
                            airtest_snapshot(driver, device, result_id)
                        )
                        performance = asyncio.run(get_performance(device, performance))
                        loop.run_until_complete(
                            airtest_log(
                                device,
                                result_id,
                                0,
                                j["name"],
                                menu_id,
                                res_log,
                                before_img,
                                after_img,
                                performance,
                                "",
                                {},
                            )
                        )
                elif j["type"] == 3:
                    try:
                        if j["name"] == "输入正确的手机号":
                            if device == "10CE6R0NP7001KX":
                                # Vivo s19(黑色1)
                                j["value"] = "19065402394"
                            elif device == "10CE970KH2002YQ":
                                # Vivo s19(白色1)
                                j["value"] = "18127803668"
                            elif device == "10AE8D2RXP001CT":
                                # Vivo s19(粉色)
                                j["value"] = "18148757543"
                            elif device == "10CE9F1UHC0037A":
                                # Vivo s19(白色2)
                                j["value"] = "19928355488"
                            elif device == "10AE650C38000QS":
                                # Vivo s19(黑色2)
                                j["value"] = "13143723397"
                            elif device == "10CE7U0CTD0023A":
                                # Vivo s19(黑色3)
                                j["value"] = "19124175810"

                        if j["name"] == "输入正确的邮箱":
                            if device == "10CE6R0NP7001KX":
                                j["value"] = "linjiyong@bluepoch.com"
                            elif device == "10CE970KH2002YQ":
                                j["value"] = "z19928355488@gmail.com"
                            elif device == "10AE8D2RXP001CT":
                                j["value"] = "ljy951697407@163.com"
                            elif device == "10CE9F1UHC0037A":
                                j["value"] = "linjiyong996@gmail.com"
                            elif device == "10AE650C38000QS":
                                j["value"] = "3110316730@qq.com"
                            elif device == "10CE7U0CTD0023A":
                                j["value"] = "ljy951697407@163.com"

                        if wait_until_exists(device, j["android"]["img"], timeout=180):
                            target = Template(j["android"]["img"])
                            touch(target)
                            text(j["value"])
                            performance = asyncio.run(
                                get_performance(device, performance)
                            )
                            after_img = asyncio.run(
                                airtest_snapshot(driver, device, result_id)
                            )
                            res_log = f"输入：{j['value']}， 成功"
                            loop.run_until_complete(
                                airtest_log(
                                    device,
                                    result_id,
                                    1,
                                    j["name"],
                                    menu_id,
                                    res_log,
                                    before_img,
                                    after_img,
                                    performance,
                                    "",
                                    {},
                                )
                            )
                        else:
                            res_log = f'{j["android"]["img"]}，图像识别失败'
                            after_img = asyncio.run(
                                airtest_snapshot(driver, device, result_id)
                            )
                            performance = asyncio.run(
                                get_performance(device, performance)
                            )
                            loop.run_until_complete(
                                airtest_log(
                                    device,
                                    result_id,
                                    0,
                                    j["name"],
                                    menu_id,
                                    res_log,
                                    before_img,
                                    after_img,
                                    performance,
                                    "",
                                    {},
                                )
                            )
                    except Exception as e:
                        res_log = f"输入：{j['value']}，失败，原因是：{str(e)}"
                        after_img = asyncio.run(
                            airtest_snapshot(driver, device, result_id)
                        )
                        performance = asyncio.run(get_performance(device, performance))
                        loop.run_until_complete(
                            airtest_log(
                                device,
                                result_id,
                                0,
                                j["name"],
                                menu_id,
                                res_log,
                                before_img,
                                after_img,
                                performance,
                                "",
                                {},
                            )
                        )
                elif j["type"] == 4:
                    try:
                        if wait_until_exists(device, j["android"]["img"], timeout=180):
                            target = Template(j["android"]["img"])
                            touch(target)
                            for i in range(20):
                                keyevent("KEYCODE_DEL")  # 清除输入框内容
                            performance = asyncio.run(
                                get_performance(device, performance)
                            )
                            after_img = asyncio.run(
                                airtest_snapshot(driver, device, result_id)
                            )
                            res_log = f"清空文本成功"
                            loop.run_until_complete(
                                airtest_log(
                                    device,
                                    result_id,
                                    1,
                                    j["name"],
                                    menu_id,
                                    res_log,
                                    before_img,
                                    after_img,
                                    performance,
                                    "",
                                    {},
                                )
                            )
                        else:
                            res_log = f'{j["android"]["img"]}，图像识别失败'
                            after_img = asyncio.run(
                                airtest_snapshot(driver, device, result_id)
                            )
                            performance = asyncio.run(
                                get_performance(device, performance)
                            )
                            loop.run_until_complete(
                                airtest_log(
                                    device,
                                    result_id,
                                    0,
                                    j["name"],
                                    menu_id,
                                    res_log,
                                    before_img,
                                    after_img,
                                    performance,
                                    "",
                                    {},
                                )
                            )
                    except Exception as e:
                        res_log = f"清空文本失败，原因是：{str(e)}"
                        after_img = asyncio.run(
                            airtest_snapshot(driver, device, result_id)
                        )
                        performance = asyncio.run(get_performance(device, performance))
                        loop.run_until_complete(
                            airtest_log(
                                device,
                                result_id,
                                0,
                                j["name"],
                                menu_id,
                                res_log,
                                before_img,
                                after_img,
                                performance,
                                "",
                                {},
                            )
                        )
                elif j["type"] == 5:
                    try:
                        if j["name"] == "输入正确的手机验证码":
                            if device == "10CE6R0NP7001KX":
                                # ViVo S19(黑色1) 19065402394
                                device_id = "6HJDU19723002103"
                                # 验证码手机：华为 nova5 pro
                            elif device == "10CE970KH2002YQ":
                                # ViVo S19(白色1) 18127803668
                                device_id = "7fb1efb"
                                # 验证码手机：oppo reno 9
                            elif device == "10AE8D2RXP001CT":
                                # ViVo S19(粉色) 18148757543
                                device_id = "f87c1a21"
                                # 验证码手机：xiaomi k40 pro
                            elif device == "10CE9F1UHC0037A":
                                # ViVo S19(白色2) 19928355488
                                device_id = "R5CW32RABBR"
                                # 验证码手机：三星 Galaxy A54 5G
                            elif device == "10AE650C38000QS":
                                # ViVo S19(黑色2) 13143723397
                                device_id = "AXYFVB1C03005594"
                                # 验证码手机：荣耀 60
                            elif device == "10CE7U0CTD0023A":
                                # ViVo S19(黑色3) 19124175810
                                device_id = "22X0219924002278"
                                # 验证码手机：华为p30 pro
                            else:
                                device_id = ""

                        sms_code = get_sms(
                            now_time=int(now_time) * 1000, device_id=device_id
                        )
                        if wait_until_exists(device, j["android"]["img"], timeout=180):
                            target = Template(j["android"]["img"])
                            touch(target)
                            text(sms_code)
                            performance = asyncio.run(
                                get_performance(device, performance)
                            )
                            after_img = asyncio.run(
                                airtest_snapshot(driver, device, result_id)
                            )
                            res_log = f"输入手机验证码：{sms_code}， 成功"
                            loop.run_until_complete(
                                airtest_log(
                                    device,
                                    result_id,
                                    1,
                                    j["name"],
                                    menu_id,
                                    res_log,
                                    before_img,
                                    after_img,
                                    performance,
                                    "",
                                    {},
                                )
                            )
                        else:
                            res_log = f'{j["android"]["img"]}，图像识别失败'
                            after_img = asyncio.run(
                                airtest_snapshot(driver, device, result_id)
                            )
                            performance = asyncio.run(
                                get_performance(device, performance)
                            )
                            loop.run_until_complete(
                                airtest_log(
                                    device,
                                    result_id,
                                    0,
                                    j["name"],
                                    menu_id,
                                    res_log,
                                    before_img,
                                    after_img,
                                    performance,
                                    "",
                                    {},
                                )
                            )
                    except Exception as e:
                        res_log = f"输入手机验证码，失败，原因是：{str(e)}"
                        after_img = asyncio.run(
                            airtest_snapshot(driver, device, result_id)
                        )
                        performance = asyncio.run(get_performance(device, performance))
                        loop.run_until_complete(
                            airtest_log(
                                device,
                                result_id,
                                0,
                                j["name"],
                                menu_id,
                                res_log,
                                before_img,
                                after_img,
                                performance,
                                "",
                                {},
                            )
                        )
                elif j["type"] == 6:
                    try:
                        if j["name"] == "关闭app，并删除差更文件":
                            device_rm_file(device)
                        after_img = asyncio.run(
                            airtest_snapshot(driver, device, result_id)
                        )
                        performance = asyncio.run(get_performance(device, performance))
                        res_log = f"关闭APP：{j['package']}, 成功"
                        loop.run_until_complete(
                            airtest_log(
                                device,
                                result_id,
                                1,
                                j["name"],
                                menu_id,
                                res_log,
                                before_img,
                                after_img,
                                performance,
                                "",
                                {},
                            )
                        )
                    except Exception as e:
                        res_log = f"关闭APP：{j['package']}, 失败，原因是：{str(e)}"
                        after_img = asyncio.run(
                            airtest_snapshot(driver, device, result_id)
                        )
                        performance = asyncio.run(get_performance(device, performance))
                        loop.run_until_complete(
                            airtest_log(
                                device,
                                result_id,
                                0,
                                j["name"],
                                menu_id,
                                res_log,
                                before_img,
                                after_img,
                                performance,
                                "",
                                {},
                            )
                        )
                elif j["type"] == 7:
                    try:
                        performance = asyncio.run(get_performance(device, performance))
                        time.sleep(2)
                        keyevent("TAB")
                        time.sleep(2)
                        if "value" in j.keys() and j["value"] != "":
                            res_log = f"输入：{j['value']}， 输入完成"
                            text(j["value"], enter=False)
                        else:
                            res_log = "Tab按键模拟成功"
                        time.sleep(2)
                        after_img = asyncio.run(
                            airtest_snapshot(driver, device, result_id)
                        )
                        loop.run_until_complete(
                            airtest_log(
                                device,
                                result_id,
                                1,
                                j["name"],
                                menu_id,
                                res_log,
                                before_img,
                                after_img,
                                performance,
                                "",
                                {},
                            )
                        )
                    except Exception as e:
                        res_log = f"Tab操作失败，原因是：{str(e)}"
                        after_img = asyncio.run(
                            airtest_snapshot(driver, device, result_id)
                        )
                        performance = asyncio.run(get_performance(device, performance))
                        loop.run_until_complete(
                            airtest_log(
                                device,
                                result_id,
                                0,
                                j["name"],
                                menu_id,
                                res_log,
                                before_img,
                                after_img,
                                performance,
                                "",
                                {},
                            )
                        )
                elif j["type"] == 8:
                    try:
                        performance = asyncio.run(get_performance(device, performance))
                        time.sleep(2)
                        keyevent("ENTER")
                        time.sleep(4)
                        if "value" in j.keys() and j["value"] != "":
                            res_log = f"输入：{j['value']}， 输入完成"
                            text(j["value"], enter=False)
                        else:
                            res_log = "回车按键模拟成功"
                        time.sleep(2)
                        after_img = asyncio.run(
                            airtest_snapshot(driver, device, result_id)
                        )
                        loop.run_until_complete(
                            airtest_log(
                                device,
                                result_id,
                                1,
                                j["name"],
                                menu_id,
                                res_log,
                                before_img,
                                after_img,
                                performance,
                                "",
                                {},
                            )
                        )
                    except Exception as e:
                        res_log = f"回车操作失败，原因是：{str(e)}"
                        after_img = asyncio.run(
                            airtest_snapshot(driver, device, result_id)
                        )
                        performance = asyncio.run(get_performance(device, performance))
                        loop.run_until_complete(
                            airtest_log(
                                device,
                                result_id,
                                0,
                                j["name"],
                                menu_id,
                                res_log,
                                before_img,
                                after_img,
                                performance,
                                "",
                                {},
                            )
                        )
                elif j["type"] == 9:
                    pass
    driver.stop_recording()
    loop.run_until_complete(
        task_end(result_id, device, total, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    performance = asyncio.run(get_performance(device, performance))
    loop.run_until_complete(
        airtest_log(
            device,
            result_id,
            1,
            "执行结束",
            menu_id,
            "自动化任务执行完成，请查看执行结果",
            "",
            "",
            performance,
            f"{source_ip}/{video}",
            {},
        )
    )

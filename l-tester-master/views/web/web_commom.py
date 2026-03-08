import asyncio
from datetime import datetime, timedelta
import json
import os
import platform
import time
from urllib.parse import urlparse
from views.web.web_model import (
    Web_element,
    Web_menu,
    Web_result_detail,
    Web_result_list,
    Web_script,
)
from pathlib import Path
from playwright.async_api import async_playwright
from config.settings import playwright_result_path, project_path
from autowing.playwright.async_fixture import create_async_fixture
from dotenv import load_dotenv


async def analysis_element(file_name, user_id, pid, data):
    try:
        script = []
        for i in data:
            script_info = {}
            action = i["action"]
            if action == "open_page":
                script_info.update(
                    {
                        "name": i["fill_name"],
                        "type": 0,
                        "children": [],
                        "action": {
                            "type": 1,
                            "input": "",
                            "assert": [],
                            "target": "",
                            "element": i["action_detail"]["open_page"]["url"],
                            "up_type": 1,
                            "sway_type": 1,
                            "target_id": "",
                            "locator": 1,
                            "locator_select": 1,
                            "target_locator": 1,
                            "target_locator_select": 1,
                            "wait_time": 1,
                            "element_id": None,
                            "target_type": 1,
                            "before_wait": 1,
                            "after_wait": 1,
                            "cookies": [],
                            "localstorage": [],
                            "timeout": 15,
                        },
                        "status": True,
                    }
                )
            elif action == "mouse_clicking":
                action_detail = i["action_detail"]["mouse_clicking"]
                element = await handle_element_value(
                    action_detail["element"]["custom_locators"]
                )
                if action_detail["type"] == "single_click_left":
                    script_info.update(
                        {
                            "name": i["fill_name"],
                            "type": 1,
                            "children": [],
                            "action": {
                                "type": 1,
                                "input": "",
                                "assert": [],
                                "target": "",
                                "element": element,
                                "up_type": 1,
                                "sway_type": 1,
                                "target_id": "",
                                "wait_time": 1,
                                "locator": 1,
                                "locator_select": 1,
                                "target_locator": 1,
                                "target_locator_select": 1,
                                "element_id": None,
                                "target_type": 1,
                                "before_wait": 1,
                                "after_wait": 1,
                                "cookies": [],
                                "localstorage": [],
                                "timeout": 15,
                            },
                            "status": True,
                        }
                    )
                elif action_detail["type"] == "double_click":
                    script_info.update(
                        {
                            "name": i["fill_name"],
                            "type": 1,
                            "children": [],
                            "action": {
                                "type": 1,
                                "input": "",
                                "assert": [],
                                "target": "",
                                "element": element,
                                "up_type": 1,
                                "sway_type": 1,
                                "target_id": "",
                                "locator": 1,
                                "locator_select": 1,
                                "target_locator": 1,
                                "target_locator_select": 1,
                                "wait_time": 1,
                                "element_id": None,
                                "target_type": 1,
                                "before_wait": 1,
                                "after_wait": 1,
                                "cookies": [],
                                "localstorage": [],
                                "timeout": 15,
                            },
                            "status": True,
                        }
                    )
                elif action_detail["type"] == "single_click_right":
                    script_info.update(
                        {
                            "name": i["fill_name"],
                            "type": 16,
                            "children": [],
                            "action": {
                                "type": 1,
                                "input": "",
                                "assert": [],
                                "target": "",
                                "element": element,
                                "up_type": 1,
                                "sway_type": 1,
                                "locator": 1,
                                "locator_select": 1,
                                "target_locator": 1,
                                "target_locator_select": 1,
                                "target_id": "",
                                "wait_time": 1,
                                "element_id": None,
                                "target_type": 1,
                                "before_wait": 1,
                                "after_wait": 1,
                                "cookies": [],
                                "localstorage": [],
                                "timeout": 15,
                            },
                            "status": True,
                        }
                    )
            elif action == "input_operations":
                action_detail = i["action_detail"]["input_operations"]
                value = action_detail["input_content"]
                element = await handle_element_value(
                    action_detail["element"]["custom_locators"]
                )
                if value != "":
                    script_info.update(
                        {
                            "name": i["fill_name"],
                            "type": 5,
                            "children": [],
                            "action": {
                                "type": 1,
                                "input": value,
                                "assert": [],
                                "target": "",
                                "element": element,
                                "up_type": 1,
                                "sway_type": 1,
                                "target_id": "",
                                "locator": 1,
                                "locator_select": 1,
                                "target_locator": 1,
                                "target_locator_select": 1,
                                "wait_time": 1,
                                "element_id": None,
                                "target_type": 1,
                                "before_wait": 1,
                                "after_wait": 1,
                                "cookies": [],
                                "localstorage": [],
                                "timeout": 15,
                            },
                            "status": True,
                        }
                    )
                else:
                    script_info.update(
                        {
                            "name": "清空文本",
                            "type": 7,
                            "children": [],
                            "action": {
                                "type": 1,
                                "input": value,
                                "assert": [],
                                "target": "",
                                "element": element,
                                "up_type": 1,
                                "sway_type": 1,
                                "target_id": "",
                                "locator": 1,
                                "locator_select": 1,
                                "target_locator": 1,
                                "target_locator_select": 1,
                                "wait_time": 1,
                                "element_id": None,
                                "target_type": 1,
                                "before_wait": 1,
                                "after_wait": 1,
                                "cookies": [],
                                "localstorage": [],
                                "timeout": 15,
                            },
                            "status": True,
                        }
                    )
            else:
                pass
            script.append(script_info)
        menu = await Web_menu.create(name=file_name, user_id=user_id, type=2, pid=pid)
        await Web_script.create(
            menu_id=menu.id,
            script=script,
            user_id=user_id,
        )
        return True, "文件导入解析成功"
    except Exception as e:
        return False, str(e)


async def handle_element_value(data):
    try:
        values = [item["value"] for item in data]
        result = ",".join(values)
        return result
    except Exception as e:
        print(f"处理元素值失败， 原因：{str(e)}")


async def analysis_web_script(data):
    try:
        script = []
        for i in data["script"]:
            script_info = await Web_script.filter(menu_id=i["id"]).first().values()
            status, msg, result = await analysis_web_script_detail(
                script_info["script"], i["id"]
            )
            script.extend(result)
        script_list = []
        for i in data["browser"]:
            script_info = {
                "script": script,
                "result_id": data["result_id"],
                "browser": i,
                "width": data["width"],
                "height": data["height"],
            }
            script_list.append(script_info)
        return status, msg, script_list, data["browser_type"]
    except Exception as e:
        print(f"解析web脚本失败， 原因：{str(e)}")
        return False, str(e)


async def analysis_web_script_detail(script, menu_id):
    try:
        result = []
        for i in script:
            i["menu_id"] = menu_id
            if i["type"] == 4:
                if i["action"]["target_type"] == 2:
                    web_element = (
                        await Web_element.filter(id=i["action"]["target_id"][-1])
                        .first()
                        .values()
                    )
                    element = web_element["element"]
                    i["action"]["target"] = element["value"]
                    if element["type"] == 1:
                        i["action"]["target_locator"] = 1
                    if element["type"] == 2:
                        if element["locator_type"] == 3:
                            i["action"]["type"] = 1
                            i["action"]["target_locator"] = 1
                        elif element["locator_type"] == 4:
                            i["action"]["target_locator"] = 2
                            i["action"]["target_locator_select"] = element[
                                "locator_select_type"
                            ]
                            i["action"]["role"] = element["locator_role_type"]
            if i["action"]["type"] == 2:
                web_element = (
                    await Web_element.filter(id=i["action"]["element_id"][-1])
                    .first()
                    .values()
                )
                element = web_element["element"]
                i["action"]["element"] = element["value"]
                if element["type"] == 1:
                    i["action"]["locator"] = 1
                if element["type"] == 2:
                    i["action"]["type"] = 1
                    if element["locator_type"] == 3:
                        i["action"]["locator"] = 1
                    elif element["locator_type"] == 4:
                        i["action"]["locator"] = 2
                        i["action"]["locator_select"] = element["locator_select_type"]
                        i["action"]["role"] = element["locator_role_type"]
            if i["children"]:
                res = await analysis_web_script_detail(i["children"], menu_id)
                i["children"] = res[2]
            result.append(i)
        return True, "任务创建成功", result
    except Exception as e:
        return False, str(e)


async def run_web_async(data, run_browser_type):
    try:
        browser_type = data["browser"]
        script = data["script"]
        result_id = data["result_id"]
        width = data["width"] if data["width"] else 1920
        height = data["height"] if data["height"] else 1080
        if run_browser_type == 1:
            headless = False
        else:
            headless = True
        try:
            async with async_playwright() as playwright:
                # 根据浏览器类型启动实例
                launch_config = {
                    1: {"browser": "chromium", "channel": "chrome"},
                    2: {"browser": "firefox", "channel": "firefox"},
                    3: {"browser": "chromium", "channel": "msedge"},
                    4: {"browser": "webkit", "channel": "webkit"},
                }
                config = launch_config.get(browser_type, {})
                BASE_APP_DIR = Path(
                    f"{playwright_result_path}/{result_id}/{browser_type}"
                )
                if not BASE_APP_DIR.exists():
                    os.makedirs(BASE_APP_DIR)
                browser = await getattr(playwright, config["browser"]).launch(
                    channel=config.get("channel"), headless=headless
                )
                context = await browser.new_context(
                    viewport={"width": width, "height": height},
                    record_video_dir=BASE_APP_DIR,
                )

                await context.tracing.start(
                    screenshots=True, snapshots=True, sources=True
                )

                #  执行脚本
                success, result = await run_script_async(
                    browser_type, script, result_id, context
                )

                # 关闭资源
                await context.close()
                await browser.close()
                # 重命名视频文件
                video_files = [
                    f for f in os.listdir(BASE_APP_DIR) if f.endswith(".webm")
                ]
                if video_files:
                    await Web_result_detail.filter(
                        result_id=result_id, browser=browser_type, log="执行结束"
                    ).update(
                        video=f"/media/playwright/{result_id}/{browser_type}/{video_files[0]}"
                    )
                    await Web_result_list.filter(result_id=result_id).update(status=1)
            return success, result
        except Exception as e:
            print(f"Playwright 执行失败: {str(e)}")
            return False, f"Playwright 执行失败: {str(e)}"
    except Exception as e:
        print(f"Playwright 执行失败: {str(e)}")
        await Web_result_list.filter(result_id=result_id).update(status=1)
        return False, f"Playwright 执行失败: {str(e)}"


async def run_script_async(browser, script, result_id, context):
    try:
        global after_img, ai
        driver = None
        el_status = False
        load_dotenv()
        ai_fixture = create_async_fixture()
        for i in script:
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status = 1
            assert_list = []
            result = False, f"元素{i['action']['element']}识别失败，未找到元素"
            if not i["status"]:
                print(f"脚本{i['name']}未执行")
                continue
            menu_id = i["menu_id"]
            if i["type"] != 0 and i["type"] != 13:
                before_img = await playwright_screenshot(driver, browser, result_id)
                await before_element_wait(
                    driver, i["name"], browser, result_id, i["action"]["before_wait"]
                )
            else:
                before_img = ""
            try:
                await write_log(f"正在执行步骤：{i['name']}", browser, result_id)
                if i["type"] == 0:
                    if i["action"]["localstorage"]:
                        await set_localstorage(
                            context, i["action"]["localstorage"], browser, result_id
                        )
                    if i["action"]["cookies"]:
                        await set_cookie(
                            context,
                            i["action"]["cookies"],
                            browser,
                            result_id,
                            i["action"]["element"],
                        )
                    result = await open_url(browser, i["action"], result_id, context)
                    driver = result[2]
                    ai = ai_fixture(page=driver)
                elif i["type"] == 1:
                    el_status, element = await handle_element(
                        driver, i["action"], result_id, browser
                    )
                    if el_status:
                        result = await element_click(
                            i["name"], browser, result_id, element
                        )
                elif i["type"] == 2:
                    el_status, element = await handle_element(
                        driver, i["action"], result_id, browser
                    )
                    if el_status:
                        result = await element_dblclick(
                            i["name"], browser, result_id, element
                        )
                elif i["type"] == 3:
                    el_status, element = await handle_element(
                        driver, i["action"], result_id, browser
                    )
                    if el_status:
                        result = await element_longclick(
                            driver, i["name"], browser, result_id, element
                        )
                elif i["type"] == 4:
                    el_status, element = await handle_element(
                        driver, i["action"], result_id, browser
                    )
                    ta_status, target = await ta_handle_element(
                        driver, i["action"], result_id, browser
                    )
                    if el_status and ta_status:
                        result = await element_drop(
                            driver, i["name"], browser, result_id, element, target
                        )
                elif i["type"] == 5:
                    el_status, element = await handle_element(
                        driver, i["action"], result_id, browser
                    )
                    if el_status:
                        result = await element_input(
                            i["name"], browser, result_id, element, i["action"]["input"]
                        )
                elif i["type"] == 6:
                    el_status, element = await handle_element(
                        driver, i["action"], result_id, browser
                    )
                    if el_status:
                        result = await element_add_input(
                            i["name"], browser, result_id, element, i["action"]["input"]
                        )
                elif i["type"] == 7:
                    el_status, element = await handle_element(
                        driver, i["action"], result_id, browser
                    )
                    if el_status:
                        result = await element_input_clear(
                            i["name"], browser, result_id, element
                        )
                elif i["type"] == 8:
                    result = await element_sway_up(
                        driver, i["name"], browser, result_id, i["action"]
                    )
                elif i["type"] == 9:
                    result = await element_sway_left(
                        driver, i["name"], browser, result_id, i["action"]
                    )
                elif i["type"] == 10:
                    if_dict = {
                        "type": i["action"]["type"],
                        "element": i["action"]["element"],
                        "locator": i["action"]["locator"],
                        "locator_select": i["action"]["locator_select"],
                        "page_type": i["action"]["target_type"],
                        "role": i["action"]["input"],
                    }
                    result = await element_if(
                        driver, i["name"], browser, result_id, if_dict, ai
                    )
                    if result[0]:
                        if i["children"]:
                            await element_for(
                                driver,
                                i["name"],
                                browser,
                                result_id,
                                1,
                                i["children"],
                                context,
                                ai,
                                ai_fixture,
                            )
                elif i["type"] == 11:
                    if i["children"]:
                        result = await element_for(
                            driver,
                            i["name"],
                            browser,
                            result_id,
                            int(i["action"]["element"]),
                            i["children"],
                            context,
                            ai,
                            ai_fixture,
                        )
                    else:
                        result = True, f"{i['name']}执行成功"
                elif i["type"] == 12:
                    result = await element_wait(
                        driver, i["name"], browser, result_id, i["action"]["element"]
                    )
                elif i["type"] == 13:
                    if i["action"]["localstorage"]:
                        await set_localstorage(
                            context, i["action"]["localstorage"], browser, result_id
                        )
                    if i["action"]["cookies"]:
                        await set_cookie(
                            context,
                            i["action"]["cookies"],
                            browser,
                            result_id,
                            i["action"]["element"],
                        )
                    result = await element_new_page(
                        context, i["name"], browser, result_id, i["action"]["element"]
                    )
                    driver = result[2]
                    context = result[3]
                    ai = ai_fixture(page=driver)
                elif i["type"] == 14:
                    result = await element_switch_page(
                        context, i["name"], browser, result_id, "previous", driver
                    )
                    driver = result[2]
                elif i["type"] == 15:
                    result = await element_switch_page(
                        context, i["name"], browser, result_id, "next", driver
                    )
                    driver = result[2]
                elif i["type"] == 17:
                    result = await element_eval(
                        driver, i["action"]["element"], result_id, browser
                    )
                    print(result)
                elif i["type"] == 18:
                    el_status, element = await handle_element(
                        driver, i["action"], result_id, browser
                    )
                    if el_status:
                        result = await element_upload_file(
                            element, i["name"], browser, result_id, i["action"]["input"]
                        )
                elif i["type"] == 19:
                    # 进行AI操作
                    i["name"] = i["action"]["element"]
                    await write_log(
                        f"开始执行AI操作：{i['action']['element']}", browser, result_id
                    )
                    result = await ai.ai_action(i["action"]["element"])
                    if result[0]:
                        await write_log(
                            f"AI操作执行成功：{i['action']['element']}",
                            browser,
                            result_id,
                        )
                    else:
                        await write_log(
                            f"AI操作执行失败：{i['action']['element']}, 原因是：{result[1]}",
                            browser,
                            result_id,
                        )
                elif i["type"] == 20:
                    # 刷新当前页面
                    await write_log(
                        f"正在刷新当前页面：{i['name']}", browser, result_id
                    )
                    reload = await driver.reload()
                    # 强制等待3秒，避免页面加载不完全
                    time.sleep(3)
                    if reload:
                        result = True, "刷新当前页面成功"
                    else:
                        result = False, "刷新当前页面失败"
                    await write_log(
                        f"刷新当前页面结果：{result[1]}", browser, result_id
                    )
                elif i["type"] == 21:
                    result = await element_close_page(
                        context,
                        i["name"],
                        browser,
                        result_id,
                        i["action"]["target"],
                        i["action"]["element"],
                        driver,
                    )
                    driver = result[2]
                    context = result[3]
                if not result[0]:
                    # 进行AI操作
                    await write_log(
                        f"{i['name']}：尝试AI补救中，开始执行AI操作：{i['name']}",
                        browser,
                        result_id,
                    )
                    result = await ai.ai_remedy(i)
                    if result[0]:
                        result = True, f"{i['name']}：AI补救成功"
                        await write_log(f"{i['name']}：AI补救成功", browser, result_id)
                    else:
                        await write_log(f"{i['name']}：AI补救失败", browser, result_id)
                after_img = await playwright_screenshot(driver, browser, result_id)
                if i["action"]["assert"]:
                    status, assert_list = await element_assert(
                        driver, browser, result_id, i["action"]["assert"], ai
                    )
                if result[0]:
                    await write_result(
                        i["name"],
                        result[1],
                        browser,
                        result_id,
                        status,
                        before_img,
                        after_img,
                        "",
                        assert_list,
                        menu_id,
                        now_time,
                        "",
                    )
                else:
                    await write_result(
                        i["name"],
                        result[1],
                        browser,
                        result_id,
                        0,
                        before_img,
                        after_img,
                        "",
                        assert_list,
                        menu_id,
                        now_time,
                        "",
                    )
                await after_element_wait(
                    driver, i["name"], browser, result_id, i["action"]["after_wait"]
                )
            except Exception as e:
                print(f"执行失败， 原因是：{str(e)}")
                after_img = await playwright_screenshot(driver, browser, result_id)
                await write_result(
                    i["name"],
                    result[1],
                    browser,
                    result_id,
                    status,
                    before_img,
                    after_img,
                    "",
                    assert_list,
                    menu_id,
                    now_time,
                    "",
                )
        time.sleep(3)
        BASE_APP_DIR = Path(f"{playwright_result_path}/{result_id}/{browser}")
        new_filename = "{}".format("trace.zip")
        trace_path = BASE_APP_DIR / new_filename
        await context.tracing.stop(path=trace_path)
        await driver.close()
        await driver.video.path()
        now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await write_result(
            "执行结束",
            "执行结束",
            browser,
            result_id,
            1,
            "",
            "",
            "",
            [],
            None,
            now_time,
            f"/media/playwright/{result_id}/{browser}/trace.zip",
        )
        await write_log(f"执行结束", browser, result_id)
        await run_end(result_id, browser)
        return True, "任务执行成功"
    except Exception as e:
        print(f"run_script任务执行失败， 原因是：{str(e)}")
        return False, str(e)


async def for_run_script_async(
    driver, browser, script, result_id, context, ai, ai_fixture
):
    el_status = False
    try:
        for i in script:
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status = 1
            assert_list = []
            result = False, f"元素{i['action']['element']}识别失败，未找到元素"
            if not i["status"]:
                print(f"脚本{i['name']}未执行")
                continue
            menu_id = i["menu_id"]
            if i["type"] != 0 or i["type"] != 13:
                before_img = await playwright_screenshot(driver, browser, result_id)
                await before_element_wait(
                    driver, i["name"], browser, result_id, i["action"]["before_wait"]
                )
            else:
                before_img = ""
            try:
                await write_log(f"正在执行步骤：{i['name']}", browser, result_id)
                if i["type"] == 0:
                    if i["action"]["localstorage"]:
                        await set_localstorage(
                            context, i["action"]["localstorage"], browser, result_id
                        )
                    if i["action"]["cookies"]:
                        await set_cookie(
                            context,
                            i["action"]["cookies"],
                            browser,
                            result_id,
                            i["action"]["element"],
                        )
                    result = await open_url(browser, i["action"], result_id, context)
                    driver = result[2]
                    ai = ai_fixture(page=driver)
                elif i["type"] == 1:
                    el_status, element = await handle_element(
                        driver, i["action"], result_id, browser
                    )
                    if el_status:
                        result = await element_click(
                            i["name"], browser, result_id, element
                        )
                elif i["type"] == 2:
                    el_status, element = await handle_element(
                        driver, i["action"], result_id, browser
                    )
                    if el_status:
                        result = await element_dblclick(
                            i["name"], browser, result_id, element
                        )
                elif i["type"] == 3:
                    el_status, element = await handle_element(
                        driver, i["action"], result_id, browser
                    )
                    if el_status:
                        result = await element_longclick(
                            driver, i["name"], browser, result_id, element
                        )
                elif i["type"] == 4:
                    el_status, element = await handle_element(
                        driver, i["action"], result_id, browser
                    )
                    ta_status, target = await ta_handle_element(
                        driver, i["action"], result_id, browser
                    )
                    if el_status and ta_status:
                        result = await element_drop(
                            driver, i["name"], browser, result_id, element, target
                        )
                elif i["type"] == 5:
                    el_status, element = await handle_element(
                        driver, i["action"], result_id, browser
                    )
                    if el_status:
                        result = await element_input(
                            i["name"], browser, result_id, element, i["action"]["input"]
                        )
                elif i["type"] == 6:
                    el_status, element = await handle_element(
                        driver, i["action"], result_id, browser
                    )
                    if el_status:
                        result = await element_add_input(
                            i["name"], browser, result_id, element, i["action"]["input"]
                        )
                elif i["type"] == 7:
                    el_status, element = await handle_element(
                        driver, i["action"], result_id, browser
                    )
                    if el_status:
                        result = await element_input_clear(
                            i["name"], browser, result_id, element
                        )
                elif i["type"] == 8:
                    result = await element_sway_up(
                        driver, i["name"], browser, result_id, i["action"]
                    )
                elif i["type"] == 9:
                    result = await element_sway_left(
                        driver, i["name"], browser, result_id, i["action"]
                    )
                elif i["type"] == 10:
                    if_dict = {
                        "type": i["action"]["type"],
                        "element": i["action"]["element"],
                        "locator": i["action"]["locator"],
                        "locator_select": i["action"]["locator_select"],
                        "page_type": i["action"]["target_type"],
                        "role": i["action"]["input"],
                    }
                    result = await element_if(
                        driver, i["name"], browser, result_id, if_dict
                    )
                    if result[0]:
                        if i["children"]:
                            await element_for(
                                driver,
                                i["name"],
                                browser,
                                result_id,
                                1,
                                i["children"],
                                context,
                                ai,
                                ai_fixture,
                            )
                elif i["type"] == 11:
                    if i["children"]:
                        result = await element_for(
                            driver,
                            i["name"],
                            browser,
                            result_id,
                            int(i["action"]["element"]),
                            i["children"],
                            context,
                            ai,
                            ai_fixture,
                        )
                    else:
                        result = True, f"{i['name']}执行成功"
                elif i["type"] == 12:
                    result = await element_wait(
                        driver, i["name"], browser, result_id, i["action"]["element"]
                    )
                elif i["type"] == 13:
                    if i["action"]["localstorage"]:
                        await set_localstorage(
                            context, i["action"]["localstorage"], browser, result_id
                        )
                    if i["action"]["cookies"]:
                        await set_cookie(
                            context,
                            i["action"]["cookies"],
                            browser,
                            result_id,
                            i["action"]["element"],
                        )
                    result = await element_new_page(
                        context, i["name"], browser, result_id, i["action"]["element"]
                    )
                    driver = result[2]
                    context = result[3]
                    ai = ai_fixture(page=driver)
                elif i["type"] == 14:
                    result = await element_switch_page(
                        context, i["name"], browser, result_id, "previous", driver
                    )
                    driver = result[2]
                elif i["type"] == 15:
                    result = await element_switch_page(
                        context, i["name"], browser, result_id, "next", driver
                    )
                    driver = result[2]
                elif i["type"] == 17:
                    result = await element_eval(
                        driver, i["action"]["element"], result_id, browser
                    )
                elif i["type"] == 18:
                    el_status, element = await handle_element(
                        driver, i["action"], result_id, browser
                    )
                    if el_status:
                        result = await element_upload_file(
                            element, i["name"], browser, result_id, i["action"]["input"]
                        )
                elif i["type"] == 19:
                    # 进行AI操作
                    i["name"] = i["action"]["element"]
                    await write_log(
                        f"开始执行AI操作：{i['action']['element']}", browser, result_id
                    )
                    result = await ai.ai_action(i["action"]["element"])
                    if result[0]:
                        await write_log(
                            f"AI操作执行成功：{i['action']['element']}",
                            browser,
                            result_id,
                        )
                    else:
                        await write_log(
                            f"AI操作执行失败：{i['action']['element']}, 原因是：{result[1]}",
                            browser,
                            result_id,
                        )
                elif i["type"] == 20:
                    # 刷新当前页面
                    await write_log(
                        f"正在刷新当前页面：{i['name']}", browser, result_id
                    )
                    reload = await driver.reload()
                    time.sleep(3)
                    if reload:
                        result = True, "刷新当前页面成功"
                    else:
                        result = False, "刷新当前页面失败"
                    await write_log(
                        f"刷新当前页面结果：{result[1]}", browser, result_id
                    )
                elif i["type"] == 21:
                    result = await element_close_page(
                        context,
                        i["name"],
                        browser,
                        result_id,
                        i["action"]["target"],
                        i["action"]["element"],
                        driver,
                    )
                    driver = result[2]
                    context = result[3]
                if not result[0]:
                    # 进行AI操作
                    await write_log(
                        f"{i['name']}：尝试AI补救中，开始执行AI操作：{i['name']}",
                        browser,
                        result_id,
                    )
                    result = await ai.ai_action(i["name"])
                    if result[0]:
                        result = True, f"{i['name']}：AI补救成功"
                        await write_log(f"{i['name']}：AI补救成功", browser, result_id)
                    else:
                        await write_log(f"{i['name']}：AI补救失败", browser, result_id)
                after_img = await playwright_screenshot(driver, browser, result_id)
                if i["action"]["assert"]:
                    status, assert_list = await element_assert(
                        driver, browser, result_id, i["action"]["assert"], ai
                    )
                if result[0]:
                    await write_result(
                        i["name"],
                        result[1],
                        browser,
                        result_id,
                        status,
                        before_img,
                        after_img,
                        "",
                        assert_list,
                        menu_id,
                        now_time,
                        "",
                    )
                else:
                    await write_result(
                        i["name"],
                        result[1],
                        browser,
                        result_id,
                        0,
                        before_img,
                        after_img,
                        "",
                        assert_list,
                        menu_id,
                        now_time,
                        "",
                    )
                await after_element_wait(
                    driver, "执行后等待", browser, result_id, i["action"]["after_wait"]
                )
            except Exception as e:
                after_img = ""
                await write_result(
                    i["name"],
                    result[1],
                    browser,
                    result_id,
                    0,
                    before_img,
                    after_img,
                    "",
                    assert_list,
                    menu_id,
                    now_time,
                    "",
                )
        return True, "for循环执行成功", driver, context
    except Exception as e:
        print(f"for_run_script任务执行失败， 原因是：{str(e)}")
        return False, str(e)


# 元素定位操作
async def handle_element(driver, action, result_id, browser):
    try:
        if "," in action["element"]:
            element_list = action["element"].split(",")
            for i in element_list:
                action["element"] = i
                await write_log(f"正在定位元素：{i}", browser, result_id)
                status, element = await locator_action(
                    driver, action, result_id, browser
                )
                if status:
                    return status, element
                await write_log(f"识别失败，未找到元素：{i}", browser, result_id)
        else:
            status, element = await locator_action(driver, action, result_id, browser)
            return status, element
        return False, f"元素{action['element']}识别失败，未找到元素"
    except Exception as e:
        print(f"handle_element任务执行失败， 原因是：{str(e)}")
        return False, str(e)


# 目标元素定位操作
async def ta_handle_element(driver, action, result_id, browser):
    try:
        if "," in action["element"]:
            element_list = action["element"].split(",")
            for i in element_list:
                action["element"] = i
                status, element = await target_locator_action(
                    driver, action, result_id, browser
                )
                await write_log(f"正在定位元素：{i}", browser, result_id)
                if status:
                    return status, element
                await write_log(f"识别失败，未找到元素：{i}", browser, result_id)
        else:
            status, element = await target_locator_action(
                driver, action, result_id, browser
            )
            return status, element
        await write_log(
            f"识别失败，未找到元素：{action['element']}", browser, result_id
        )
        return False, f"元素{action['element']}识别失败，未找到元素"
    except Exception as e:
        print(f"handle_element任务执行失败， 原因是：{str(e)}")
        return False, str(e)


# 元素定位操作
async def locator_action(driver, action, result_id, browser):
    try:
        await write_log(f"开始判断元素定位方式", browser, result_id)
        element_value = action["element"]
        if action["locator"] == 1:
            await write_log(
                f"正在使用定位器，开始定位元素：{action['element']}", browser, result_id
            )
            element = driver.locator(element_value)
        if action["locator"] == 2:
            await write_log(
                f"正在使用选择器，开始定位元素：{action['element']}", browser, result_id
            )
            if action["locator_select"] == 1:
                element = driver.locator(f"#{element_value}")
            elif action["locator_select"] == 2:
                element = driver.get_by_text(element_value)
            elif action["locator_select"] == 3:
                element = driver.get_by_label(element_value)
            elif action["locator_select"] == 4:
                element = driver.get_by_title(element_value)
            elif action["locator_select"] == 5:
                element = driver.get_by_placeholder(element_value, exact=True)
            elif action["locator_select"] == 6:
                element = driver.get_by_alt_text(element_value)
            elif action["locator_select"] == 7:
                element = driver.get_by_role(action["role"], name=element_value)
        await element.wait_for(state="visible", timeout=action["timeout"] * 1000)
        if await element.is_visible():
            return True, element
        return False, f"元素{element_value}识别失败，未找到元素"
    except Exception as e:
        await write_log(f"元素定位失败， 原因是：{str(e)}", browser, result_id)
        print(f"locator_action异常：{str(e)}")
        return str(e)


# 目标元素定位操作
async def target_locator_action(driver, action, result_id, browser):
    try:
        await write_log(f"开始判断目标元素定位方式", browser, result_id)
        element_value = action["target"]
        if action["target_locator"] == 1:
            await write_log(
                f"正在使用定位器，开始定位目标元素：{action['target']}",
                browser,
                result_id,
            )
            element = driver.locator(element_value)
        if action["target_locator"] == 2:
            await write_log(
                f"正在使用选择器，开始定位目标元素：{action['target']}",
                browser,
                result_id,
            )
            if action["target_locator_select"] == 1:
                element = await driver.locator(f"#{element_value}")
            elif action["target_locator_select"] == 2:
                element = await driver.get_by_text(element_value)
            elif action["target_locator_select"] == 3:
                element = await driver.get_by_label(element_value)
            elif action["target_locator_select"] == 4:
                element = await driver.get_by_title(element_value)
            elif action["target_locator_select"] == 5:
                element = await driver.get_by_placeholder(element_value, exact=True)
            elif action["locator_select"] == 6:
                element = driver.get_by_alt_text(element_value)
            elif action["locator_select"] == 7:
                element = driver.get_by_role(action["role"], name=element_value)
        await element.wait_for(state="visible", timeout=action["timeout"] * 1000)
        if await element.is_visible():
            return True, element
        return element
    except Exception as e:
        await write_log(f"目标元素定位失败， 原因是：{str(e)}", browser, result_id)
        print(f"target_locator_action异常：{str(e)}")
        return str(e)


# 断言元素定位操作
async def assert_locator_action(driver, action, result_id, browser):
    try:
        await write_log(f"开始判断元素定位方式", browser, result_id)
        element_value = action["element"]
        if action["locator"] == 1:
            await write_log(
                f"正在使用定位器，开始定位元素：{action['element']}", browser, result_id
            )
            element = driver.locator(element_value)
        if action["locator"] == 2:
            await write_log(
                f"正在使用选择器，开始定位元素：{action['element']}", browser, result_id
            )
            if action["locator_select"] == 1:
                element = await driver.locator(f"#{element_value}")
            elif action["locator_select"] == 2:
                element = await driver.get_by_text(text=element_value)
            elif action["locator_select"] == 3:
                element = await driver.get_by_label(text=element_value)
            elif action["locator_select"] == 4:
                element = await driver.get_by_title(text=element_value)
            elif action["locator_select"] == 5:
                element = await driver.get_by_placeholder(
                    text=element_value, exact=True
                )
            elif action["locator_select"] == 6:
                element = await driver.get_by_alt_text(text=element_value)
            elif action["locator_select"] == 7:
                element = await driver.get_by_role(
                    role=action["role"], text=element_value
                )
        return element
    except Exception as e:
        await write_log(f"元素定位失败， 原因是：{str(e)}", browser, result_id)
        print(f"assert_locator_action异常：{str(e)}")
        return str(e)


# 执行自定义脚本操作
async def element_eval(driver, element, result_id, browser):
    try:
        from playwright.async_api import expect

        await write_log(f"正在执行自定义脚本：{element}", browser, result_id)
        await eval(element)
        await write_log(f"执行自定义脚本成功", browser, result_id)
        return True, f"执行自定义脚本成功: {element}"
    except Exception as e:
        print(f"element_eval异常：{str(e)}")
        await write_log(f"执行自定义脚本失败， 原因是：{str(e)}", browser, result_id)
        return False, str(e)


# 打开网页操作
async def open_url(browser, action, result_id, context):
    try:
        driver = await context.new_page()
        url = action["element"]
        await driver.goto(url, wait_until="networkidle")
        result = f"网页打开成功，网页地址：{url}"
        time.sleep(3)
        await write_log(result, browser, result_id)
        return True, result, driver
    except Exception as e:
        result = f"网页打开失败，原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result, driver


# 设置localStorage操作
async def set_localstorage(context, localstorage, browser, result_id):
    try:
        result = f"开始设置localStorage"
        await write_log(result, browser, result_id)
        for i in localstorage:
            await context.add_init_script(
                script=f"""localStorage.setItem('{i["name"]}', '{i["value"]}');"""
            )
            result = f"localStorage设置成功,  key={i['name']}, value={i['value']}"
            await write_log(result, browser, result_id)
        return True
    except Exception as e:
        result = f"localStorage设置失败，原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False


# 设置cookie操作
async def set_cookie(context, cookies, browser, result_id, url):
    try:
        result = f"开始设置cookie"
        parsed_url = urlparse(url)
        await write_log(result, browser, result_id)
        for i in cookies:
            i["url"] = f"{parsed_url.scheme}://{parsed_url.netloc}"
        await context.add_cookies(cookies)
        for j in cookies:
            result = f"cookie设置成功, key={j['name']}, value={j['value']}"
            await write_log(result, browser, result_id)
        return True
    except Exception as e:
        result = f"cookie设置失败，原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False


# 点击操作
async def element_click(name, browser, result_id, element):
    try:
        await element.click()
        await write_log(f"元素定位成功， 元素：{element}", browser, result_id)
        result = f"{name}：元素点击成功"
        await write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result


# 双击操作
async def element_dblclick(name, browser, result_id, element):
    try:
        await element.dblclick()
        await write_log(f"元素定位成功， 元素：{element}", browser, result_id)
        result = f"{name}：元素双击成功"
        await write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result


# 长按操作
async def element_longclick(driver, name, browser, result_id, element):
    try:
        await element.hover()
        await driver.mouse.down(button="left")
        await driver.wait_for_timeout(2500)
        await driver.mouse.up()
        await write_log(f"元素定位成功， 元素：{element}", browser, result_id)
        result = f"{name}：元素长按成功"
        await write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result


# 拖拽操作
async def element_drop(driver, name, browser, result_id, element, target):
    try:
        from_box = await element.bounding_box()
        await driver.mouse.move(
            from_box["x"] + from_box["width"] / 2,
            from_box["y"] + from_box["height"] / 2,
        )
        await driver.mouse.down()
        await write_log(f"拖拽起始元素定位成功， 元素：{element}", browser, result_id)
        target_box = await target.bounding_box()
        await driver.mouse.move(
            target_box["x"] + target_box["width"] / 2,
            target_box["y"] + target_box["height"] / 2,
        )
        await driver.mouse.up()
        await write_log(f"拖拽目标元素定位成功， 元素：{target}", browser, result_id)
        result = f"{name}：元素拖拽成功"
        await write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result


# 输入操作
async def element_input(name, browser, result_id, element, input_value):
    try:
        await element.fill(input_value)
        await write_log(f"元素定位成功， 元素：{element}", browser, result_id)
        result = f"{name}：输入值--{input_value}--成功"
        await write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result


# 补充输入操作
async def element_add_input(name, browser, result_id, element, input_value):
    try:
        old_text = await element.input_value()
        new_text = old_text + input_value
        await element.fill(new_text)
        await write_log(f"元素定位成功， 元素：{element}", browser, result_id)
        result = f"{name}：补充输入值--{input_value}--成功"
        await write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result


# 清空文本操作
async def element_input_clear(name, browser, result_id, element):
    try:
        await element.fill("")
        await write_log(f"元素定位成功， 元素：{element}", browser, result_id)
        result = f"{name}：清空文本--成功"
        await write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result


# 上下滑动操作
async def element_sway_up(driver, name, browser, result_id, action):
    try:
        num = int(action["element"])
        if action["up_type"] == 1:
            await driver.mouse.wheel(0, delta_y=-num)
            result = f"{name}：向上滑动像素--{num}--成功"
        else:
            await driver.mouse.wheel(0, delta_y=num)
            result = f"{name}：向下滑动像素--{num}--成功"
        time.sleep(3)
        await write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result


# 左右滑动操作
async def element_sway_left(driver, name, browser, result_id, action):
    try:
        num = int(action["element"])
        if action["sway_type"] == 1:
            await driver.scroll_by(0, num)
            result = f"{name}：向做滑动像素--{num}--成功"
        else:
            await driver.scroll_by(0, -num)
            result = f"{name}：向右滑动像素--{num}--成功"
        await write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result


# if判断操作
async def element_if(driver, name, browser, result_id, if_dict, ai):
    try:
        if_list = []
        if_list.append(if_dict)
        assert_result = await element_assert(driver, browser, result_id, if_list, ai)
        if assert_result[0] == 1:
            result = f"{name}：判断成功，元素存在"
            await write_log(result, browser, result_id)
            return True, result
        else:
            result = f"{name}：判断失败，元素不存在"
            await write_log(result, browser, result_id)
            return False, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result


# 循环执行操作
async def element_for(driver, name, browser, result_id, num, script, context, ai):
    try:
        for i in range(0, num):
            await for_run_script_async(driver, browser, script, result_id, context, ai)
        result = f"{name}：执行成功"
        await write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result


# 等待操作
async def element_wait(driver, name, browser, result_id, wait_time):
    try:
        await driver.wait_for_timeout(int(wait_time))
        result = f"{name}：等待--{wait_time}秒--成功"
        await write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result


# 执行前等待操作
async def before_element_wait(driver, name, browser, result_id, wait_time):
    try:
        await driver.wait_for_timeout(int(wait_time))
        result = f"{name}：执行前等待--{wait_time}秒--成功"
        await write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行前等待失败 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result


# 执行后等待操作
async def after_element_wait(driver, name, browser, result_id, wait_time):
    try:
        await driver.wait_for_timeout(int(wait_time))
        result = f"{name}：执行后等待--{wait_time}秒--成功"
        await write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行后等待 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result


# 打开新窗口操作
async def element_new_page(context, name, browser, result_id, element):
    try:
        time.sleep(3)
        driver = await context.new_page()
        await driver.goto(element)
        result = f"{name}：打开新窗口--{element}--成功"
        await write_log(result, browser, result_id)
        return True, result, driver, context
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result, driver, context


# 切换标签页操作
async def element_switch_page(context, name, browser, result_id, direction, driver):
    try:
        all_pages = context.pages
        for i in all_pages:
            if i == driver:
                current_index = all_pages.index(i)
        if direction == "next":
            # 切换到下一个标签页
            if current_index < len(all_pages) - 1:
                next_page = all_pages[current_index + 1]
                await next_page.bring_to_front()  # 切换到下一个页面
                result = f"切换到下一个标签页，成功"
                await write_log(result, browser, result_id)
                return True, result, next_page
            else:
                result = "执行失败，已经是最后一个标签页，无法向下切换"
                await write_log(result, browser, result_id)
                return False, result, driver
        elif direction == "previous":
            # 切换到上一个标签页
            if current_index > 0:
                previous_page = all_pages[current_index - 1]
                await previous_page.bring_to_front()  # 切换到上一个页面
                result = f"切换到上一个标签页，成功"
                await write_log(result, browser, result_id)
                return True, result, previous_page
            else:
                await write_log(result, browser, result_id)
                result = "执行失败，已经是第一个标签页，无法向下切换"
                return False, result, driver
        else:
            result = "执行失败，无效的方向，方向应为 'next' 或 'previous'"
        await write_log(result, browser, result_id)
        return False, result, driver
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result


# 关闭标签页操作
async def element_close_page(
    context, name, browser, result_id, direction, n: None, driver
):
    try:
        # 获取所有标签页
        all_pages = context.pages
        current_index = next(
            (i for i, page in enumerate(all_pages) if page == driver), -1
        )

        # 记录调试信息
        await write_log(
            f"关闭页面操作: 当前页面索引={current_index}, 总页面数={len(all_pages)}, 方向={direction}",
            browser,
            result_id,
        )

        # 处理关闭当前页面的情况 (最常见情况)
        if direction == "now":
            if current_index == -1:
                return False, "执行失败，当前页面不存在", driver, context

            # 关闭当前页面
            await driver.close()
            remaining_pages = context.pages

            # 确定新的活动页面
            if remaining_pages:
                # 优先选择下一个页面，如果没有则选择前一个
                new_index = min(current_index, len(remaining_pages) - 1)
                new_driver = remaining_pages[new_index]
                await new_driver.bring_to_front()
                result = "成功关闭当前页面并切换到新页面"
            else:
                # 所有页面都关闭时创建新页面
                new_driver = await context.new_page()
                await new_driver.goto("about:blank")
                result = "所有标签页已关闭，已创建新页面"

            await write_log(result, browser, result_id)
            return True, result, new_driver, context

        # 处理关闭其他页面的情况
        try:
            # 确定目标页面索引
            if direction == "next":
                target_index = current_index + 1
            elif direction == "previous":
                target_index = current_index - 1
            elif direction == "customize":
                target_index = n - 1
            else:
                return False, f"无效的方向: {direction}", driver, context

            # 验证目标索引
            if target_index < 0 or target_index >= len(all_pages):
                return False, f"目标页面索引 {target_index} 超出范围", driver, context

            # 关闭目标页面
            target_page = all_pages[target_index]
            await target_page.close()
            result = f"成功关闭{direction}方向的页面"

            # 如果关闭的是当前页面，需要切换到新页面
            if target_index == current_index:
                remaining_pages = context.pages
                if remaining_pages:
                    new_index = min(current_index, len(remaining_pages) - 1)
                    driver = remaining_pages[new_index]
                    await driver.bring_to_front()
                    result += "并切换到新页面"

            await write_log(result, browser, result_id)
            return True, result, driver, context

        except Exception as e:
            error_msg = f"关闭{direction}页面失败: {str(e)}"
            await write_log(error_msg, browser, result_id)
            return False, error_msg, driver, context

    except Exception as e:
        error_msg = f"{name}操作失败: {str(e)}"
        await write_log(error_msg, browser, result_id)
        return False, error_msg, driver, context


async def element_upload_file(driver, name, browser, result_id, element):
    try:
        await write_log(f"正在执行上传文件文件：{element}", browser, result_id)
        await driver.set_input_files(f"{project_path}{element}")
        await write_log(f"执行上传文件成功", browser, result_id)
        return True, f"执行上传文件成功"
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        await write_log(result, browser, result_id)
        return False, result


async def assert_eval(driver, element, result_id, browser):
    try:
        from playwright.async_api import expect

        await write_log(f"正在执行断言脚本：{element}", browser, result_id)
        await eval(element)
        await write_log(f"执行自定义断言成功", browser, result_id)
        return True, f"执行断言脚本成功"
    except Exception as e:
        await write_log(f"执行断言脚本失败， 原因是：{str(e)}", browser, result_id)
        return False, str(e)


async def element_assert(driver, browser, result_id, assert_list, ai):
    status = 1
    for i in assert_list:
        try:
            i["img"] = await playwright_screenshot(driver, browser, result_id)
            if i["type"] == 1:
                element = await assert_locator_action(driver, i, result_id, browser)
                await write_log(
                    f"开始断言元素：{element}， 预期：元素存在", browser, result_id
                )
                if await element.is_visible():
                    result = f"断言成功，元素：{element}--元素存在"
                    i["status"] = 1
                    i["result"] = result
                    await write_log(result, browser, result_id)
                else:
                    status = 0
                    result = f"断言失败，元素：{element}--元素不存在"
                    i["status"] = 0
                    i["result"] = result
                    await write_log(result, browser, result_id)
            elif i["type"] == 2:
                element = await assert_locator_action(driver, i, result_id, browser)
                await write_log(
                    f"开始断言元素：{element}， 预期：元素不存在", browser, result_id
                )
                if await element.is_visible():
                    status = 0
                    result = f"断言失败，元素：{element}--元素存在"
                    i["status"] = 0
                    i["result"] = result
                    await write_log(result, browser, result_id)
                else:
                    result = f"断言成功，元素：{element}--元素不存在"
                    i["status"] = 1
                    i["result"] = result
                    await write_log(result, browser, result_id)
            elif i["type"] == 3:
                element = await driver.content()
                await write_log(
                    f"开始断言文本：{element}， 预期：文本存在", browser, result_id
                )
                if i["element"] in element:
                    result = f"断言成功，文本：{element}--文本存在"
                    i["status"] = 1
                    i["result"] = result
                    await write_log(result, browser, result_id)
                else:
                    status = 0
                    result = f"断言失败，文本：{element}--文本不存在"
                    i["status"] = 0
                    i["result"] = result
                    await write_log(result, browser, result_id)
            elif i["type"] == 4:
                element = await driver.content()
                await write_log(
                    f"开始断言文本：{element}， 预期：文本不存在", browser, result_id
                )
                if i["element"] in element:
                    status = 0
                    result = f"断言失败，文本：{element}--文本存在"
                    i["status"] = 0
                    i["result"] = result
                    await write_log(result, browser, result_id)
                else:
                    result = f"断言成功，文本：{element}--文本不存在"
                    i["status"] = 1
                    i["result"] = result
                    await write_log(result, browser, result_id)
            elif i["type"] == 5:
                title = await driver.title()
                url = driver.url
                if i["page_type"] == 2:
                    await write_log(
                        f"开始断言网页标题：{title}， 预期：标题一致",
                        browser,
                        result_id,
                    )
                    if title == i["element"]:
                        result = f"断言成功，网页标题：{title}--标题一致"
                        i["status"] = 1
                        i["result"] = result
                        await write_log(result, browser, result_id)
                    else:
                        status = 0
                        result = f"断言失败，网页标题：{title}，预期：{i['element']}--标题不一致"
                        i["status"] = 0
                        i["result"] = result
                        await write_log(result, browser, result_id)
                elif i["page_type"] == 1:
                    await write_log(
                        f"开始断言网址：{url}， 预期：网址一致", browser, result_id
                    )
                    if url == i["element"]:
                        result = f"断言成功，网址：{url}--网址一致"
                        i["status"] = 1
                        i["result"] = result
                        await write_log(result, browser, result_id)
                    else:
                        status = 0
                        result = (
                            f"断言失败，网址：{url}，预期：{i['element']}--网址不一致"
                        )
                        i["status"] = 0
                        i["result"] = result
                        await write_log(result, browser, result_id)
            elif i["type"] == 6:
                await write_log(
                    f"开始执行自定义脚本断言：{i['element']}", browser, result_id
                )
                result = await assert_eval(driver, i["element"], result_id, browser)
                if result[0]:
                    i["status"] = 1
                    i["result"] = f"断言成功，自定义脚本断言：{i['element']}--断言成功"
                    await write_log(i["result"], browser, result_id)
                else:
                    status = 0
                    i["status"] = 0
                    i["result"] = f"断言失败，自定义脚本断言：{i['element']}--断言失败"
                    await write_log(result, browser, result_id)
            elif i["type"] == 7:
                await write_log(f"开始执行AI断言：{i['element']}", browser, result_id)
                result = await ai.ai_assert(i["element"])
                if result:
                    i["status"] = 1
                    i["result"] = f"断言成功，AI断言：{i['element']}--断言成功"
                    await write_log(i["result"], browser, result_id)
                else:
                    status = 0
                    i["status"] = 0
                    i["result"] = f"断言失败，AI断言：{i['element']}--断言失败"
                    await write_log(result, browser, result_id)
        except Exception as e:
            status = 0
            i["status"] = 0
            i["result"] = f"断言失败，原因是：{str(e)}"
            await write_log(i["result"], browser, result_id)
    return status, assert_list


async def playwright_screenshot(driver, browser, result_id):
    try:
        BASE_APP_DIR = Path(f"{playwright_result_path}/{result_id}/{browser}")
        if not BASE_APP_DIR.exists():
            os.makedirs(BASE_APP_DIR)
        new_filename = "{}_{}_{}".format(
            browser, datetime.now().strftime("%Y%m%d%H%M%S%f"), "web.png"
        )
        path = BASE_APP_DIR / new_filename
        await driver.screenshot(path=path)
        return f"/media/playwright/{result_id}/{browser}/{new_filename}"
    except Exception as e:
        print(f"截图失败， 原因是：{str(e)}")


async def write_log(result, browser, result_id):
    try:
        BASE_APP_DIR = Path(f"{playwright_result_path}/{result_id}/{browser}")
        if not BASE_APP_DIR.exists():
            os.makedirs(BASE_APP_DIR)
        path = BASE_APP_DIR / f"{browser}_result.txt"
        with open(path, "a") as file:
            file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {result} \n")
    except Exception as e:
        print(f"结果写入文件失败， 原因是：{str(e)}")


async def write_result(
    name,
    log,
    browser,
    result_id,
    status,
    before_img,
    after_img,
    video,
    assert_result,
    menu_id,
    now_time,
    trace,
):
    try:
        await Web_result_detail.create(
            name=name,
            result_id=result_id,
            browser=browser,
            log=log,
            status=status,
            before_img=before_img,
            after_img=after_img,
            video=video,
            assert_result=assert_result,
            menu_id=menu_id,
            create_time=now_time,
            trace=trace,
        )
    except Exception as e:
        print(
            name,
            log,
            browser,
            result_id,
            status,
            before_img,
            after_img,
            video,
            assert_result,
            menu_id,
            trace,
        )
        print(f"write_result异常：{str(e)}")


async def run_end(result_id, browser):
    try:
        run_false = 0
        detail = await Web_result_detail.filter(result_id=result_id, browser=browser)
        total = len(detail) - 1
        for i in detail:
            if i.status == 0:
                run_false += 1
        run_true = total - run_false
        result = {
            "browser": browser,
            "total": total,
            "run_true": run_true,
            "run_false": run_false,
        }
        data = await Web_result_list.filter(result_id=result_id).first().values()
        data["result"].append(result)
        await Web_result_list.filter(result_id=result_id).update(
            result=data["result"], end_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    except Exception as e:
        print(f"run_end异常：{str(e)}")


async def parse_timestamp(line):
    # 解析时间戳
    try:
        # 提取每行开头的时间戳部分
        timestamp_str = line.split(" ")[0] + " " + line.split(" ")[1]
        return True, int(
            datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").timestamp()
        )
    except Exception as e:
        # 如果某一行没有时间戳或格式不正确，返回 None
        return False, e


async def time_add(time):
    try:
        original_time = datetime.strptime(str(time), "%Y-%m-%d %H:%M:%S")
        new_time = original_time + timedelta(seconds=3)
        return new_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print("增加3秒失败：", e)
        return time


async def filter_by_time_range(lines, start_time, end_time):
    # 根据时间范围筛选内容
    start = int(datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").timestamp())
    end = int(datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").timestamp())
    filtered_lines = []
    for line in lines:
        status, log_time = await parse_timestamp(line)
        if status:
            if start <= log_time <= end:
                filtered_lines.append(line)
    return filtered_lines

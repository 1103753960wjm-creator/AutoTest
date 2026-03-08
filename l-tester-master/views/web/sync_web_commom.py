import asyncio
import time
from datetime import datetime
import json
import os
from urllib.parse import urlparse
from views.web.web_model import Web_element, Web_menu, Web_result_detail, Web_result_list, Web_script
from pathlib import Path
from playwright.sync_api import sync_playwright
from config.settings import playwright_result_path, project_path
from autowing.playwright.fixture import create_fixture
from dotenv import load_dotenv

def async_run_web(data, run_browser_type):
    try:
        browser_type = data["browser"]
        script = data["script"]
        result_id = data["result_id"]
        width, height = data["width"] if data["width"] else 1920, data["height"] if data["height"] else 1080
        if run_browser_type == 1:
            headless = False
        else:
            headless = True
        with sync_playwright() as playwright:
            # 根据浏览器类型启动实例
            launch_config = {
                1: {"browser": "chromium", "channel": "chrome"},
                2: {"browser": "firefox", "channel": "firefox"},
                3: {"browser": "chromium", "channel": "msedge"},
                4: {"browser": "webkit", "channel": "webkit"}
            }
            config = launch_config.get(browser_type, {})
            BASE_APP_DIR = Path(f"{playwright_result_path}/{result_id}/{browser_type}")
            if not BASE_APP_DIR.exists():
                os.makedirs(BASE_APP_DIR)
            browser = getattr(playwright, config["browser"]).launch(
                channel=config.get("channel"), headless=headless)
            context = browser.new_context(viewport={'width': width, 'height': height}, record_video_dir=BASE_APP_DIR)

            context.tracing.start(screenshots=True, snapshots=True, sources=True)

            #  执行脚本
            success, result = run_script_async(browser_type, script, result_id, context)

            # 关闭资源
            context.close()
            browser.close()
            # 重命名视频文件
            video_files = [f for f in os.listdir(BASE_APP_DIR) if f.endswith(".webm")]
            if video_files:
                asyncio.run(Web_result_detail.filter(result_id=result_id, browser=browser_type, log="执行结束").update(video=f"/media/playwright/{result_id}/{browser_type}/{video_files[0]}"))
            return success, result
    except Exception as e:
        print(f"Playwright 执行失败: {str(e)}")
        return False, f"Playwright 执行失败: {str(e)}"

def run_script_async(browser, script, result_id, context):
    try:
        global after_img, ai
        driver = None
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
                before_img = playwright_screenshot(driver, browser, result_id)
                before_element_wait(driver, i["name"], browser, result_id, i["action"]["before_wait"])
            else:
                before_img = ""
            try:
                write_log(f"正在执行步骤：{i['name']}", browser, result_id)
                if i["type"] == 0:
                    if i["action"]["localstorage"]:
                        set_localstorage(context, i["action"]["localstorage"], browser, result_id)
                    if i["action"]["cookies"]:
                        set_cookie(context, i["action"]["cookies"], browser, result_id, i["action"]["element"])
                    result = open_url(browser, i["action"], result_id, context)
                    driver = result[2]
                    load_dotenv()
                    ai_fixture = create_fixture()
                    ai = ai_fixture(page=driver)
                    ai_data = [
                        "用户名输入框输入'admin'",
                        "密码输入框输入'slhd.999'",
                        "点击登录"
                        ]
                    for i in ai_data:
                        print(f"执行操作：{i}")
                        ai.ai_action(i)
                        time.sleep(2)
                        print("操作执行完毕")
                elif i["type"] == 1:
                    el_status, element = handle_element(driver, i["action"], result_id, browser)
                    if el_status:
                        result = element_click(i["name"], browser, result_id, element)
                elif i["type"] == 2:
                    el_status, element = handle_element(driver, i["action"], result_id, browser)
                    if el_status:
                        result = element_dblclick(i["name"], browser, result_id, element)
                elif i["type"] == 3:
                    el_status, element = handle_element(driver, i["action"], result_id, browser)
                    if el_status:
                        result = element_longclick(driver, i["name"], browser, result_id, element)
                elif i["type"] == 4:
                    el_status, element = handle_element(driver, i["action"], result_id, browser)
                    ta_status, target = ta_handle_element(driver, i["action"], result_id, browser)
                    if el_status and ta_status:
                        result = element_drop(driver, i["name"], browser, result_id, element, target)
                elif i["type"] == 5:
                    el_status, element = handle_element(driver, i["action"], result_id, browser)
                    if el_status:
                        result = element_input(i["name"], browser, result_id, element, i["action"]["input"])
                elif i["type"] == 6:
                    el_status, element = handle_element(driver, i["action"], result_id, browser)
                    if el_status:
                        result = element_add_input(i["name"], browser, result_id, element, i["action"]["input"])
                elif i["type"] == 7:
                    el_status, element = handle_element(driver, i["action"], result_id, browser)
                    if el_status:
                        result = element_input_clear(i["name"], browser, result_id, element)
                elif i["type"] == 8:
                    result = element_sway_up(driver, i["name"], browser, result_id, i["action"])
                elif i["type"] == 9:
                    result = element_sway_left(driver, i["name"], browser, result_id, i["action"])
                elif i["type"] == 10:
                    if_dict = {
                        "type": i["action"]["type"], "element": i["action"]["element"],
                        "locator": i["action"]["locator"], "locator_select": i["action"]["locator_select"],
                        "page_type": i["action"]["target_type"], "role": i["action"]["input"],
                    }
                    result = element_if(driver, i["name"], browser, result_id, if_dict)
                    if result[0]:
                        if i["children"]:
                            element_for(driver, i["name"], browser, result_id, 1, i["children"], context)
                elif i["type"] == 11:
                    if i["children"]:
                        result = element_for(driver, i["name"], browser, result_id, int(i["action"]["element"]), i["children"], context)
                    else:
                        result = True, f"{i['name']}执行成功"
                elif i["type"] == 12:
                    result = element_wait(driver, i["name"], browser, result_id, i["action"]["element"])
                elif i["type"] == 13:
                    if i["action"]["localstorage"]:
                        set_localstorage(context, i["action"]["localstorage"], browser, result_id)
                    if i["action"]["cookies"]:
                        set_cookie(context, i["action"]["cookies"], browser, result_id, i["action"]["element"])
                    result = element_new_page(context, i["name"], browser, result_id, i["action"]["element"])
                    driver = result[2]
                    context = result[3]
                elif i["type"] == 14:
                    result = element_switch_page(context, i["name"], browser, result_id, "previous", driver)
                    driver = result[2]
                elif i["type"] == 15:
                    result = element_switch_page(context, i["name"], browser, result_id, "next", driver)
                    driver = result[2]
                elif i["type"] == 17:
                    result = element_eval(driver, i["action"]["element"], result_id, browser)
                    print(result)
                elif i["type"] == 18:
                    el_status, element = handle_element(driver, i["action"], result_id, browser)
                    if el_status:
                        result = element_upload_file(element, i["name"], browser, result_id, i["action"]["input"])
                if i["action"]["assert"]:
                    status, assert_list = element_assert(driver, browser, result_id, i["action"]["assert"])
                after_img = playwright_screenshot(driver, browser, result_id)
                if result[0]:
                    write_result(i["name"], result[1], browser, result_id, status, before_img, after_img, "", assert_list, menu_id, now_time, "")
                else:
                    write_result(i["name"], result[1], browser, result_id, 0, before_img, after_img, "", assert_list, menu_id, now_time, "")
                after_element_wait(driver, i["name"], browser, result_id, i["action"]["after_wait"])
            except Exception as e:
                print(f"执行失败， 原因是：{str(e)}")
                after_img = playwright_screenshot(driver, browser, result_id)
                write_result(i["name"], result[1], browser, result_id, status, before_img, after_img, "", assert_list, menu_id, now_time, "")
        BASE_APP_DIR = Path(f"{playwright_result_path}/{result_id}/{browser}")
        new_filename = '{}'.format("trace.zip")
        trace_path = BASE_APP_DIR / new_filename
        context.tracing.stop(path=trace_path)
        driver.close()
        driver.video.path()
        now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        write_result("执行结束", "执行结束", browser, result_id, 1, "", "", "", [], None, now_time, f"/media/playwright/{result_id}/{browser}/trace.zip")
        write_log(f"执行结束", browser, result_id)
        run_end(result_id, browser)
        return True, "任务执行成功"
    except Exception as e:
        print(f"run_script任务执行失败， 原因是：{str(e)}")
        return False, str(e)

def for_run_script_async(driver, browser, script, result_id, context):
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
                before_img = playwright_screenshot(driver, browser, result_id)
                before_element_wait(driver, i["name"], browser, result_id, i["action"]["before_wait"])
            else:
                before_img = ""
            try:
                write_log(f"正在执行步骤：{i['name']}", browser, result_id)
                if i["type"] == 0:
                    if i["action"]["localstorage"]:
                        set_localstorage(context, i["action"]["localstorage"], browser, result_id)
                    if i["action"]["cookies"]:
                        set_cookie(context, i["action"]["cookies"], browser, result_id, i["action"]["element"])
                    result = open_url(browser, i["action"], result_id, context)
                    driver = result[2]
                elif i["type"] == 1:
                    el_status, element = handle_element(driver, i["action"], result_id, browser)
                    if el_status:
                        result = element_click(i["name"], browser, result_id, element)
                elif i["type"] == 2:
                    el_status, element = handle_element(driver, i["action"], result_id, browser)
                    if el_status:
                        result = element_dblclick(i["name"], browser, result_id, element)
                elif i["type"] == 3:
                    el_status, element = handle_element(driver, i["action"], result_id, browser)
                    if el_status:
                        result = element_longclick(driver, i["name"], browser, result_id, element)
                elif i["type"] == 4:
                    el_status, element = handle_element(driver, i["action"], result_id, browser)
                    ta_status, target = ta_handle_element(driver, i["action"], result_id, browser)
                    if el_status and ta_status:
                        result = element_drop(driver, i["name"], browser, result_id, element, target)
                elif i["type"] == 5:
                    el_status, element = handle_element(driver, i["action"], result_id, browser)
                    if el_status:
                        result = element_input(i["name"], browser, result_id, element, i["action"]["input"])
                elif i["type"] == 6:
                    el_status, element = handle_element(driver, i["action"], result_id, browser)
                    if el_status:
                        result = element_add_input(i["name"], browser, result_id, element, i["action"]["input"])
                elif i["type"] == 7:
                    el_status, element = handle_element(driver, i["action"], result_id, browser)
                    if el_status:
                        result = element_input_clear(i["name"], browser, result_id, element)
                elif i["type"] == 8:
                    result = element_sway_up(driver, i["name"], browser, result_id, i["action"])
                elif i["type"] == 9:
                    result = element_sway_left(driver, i["name"], browser, result_id, i["action"])
                elif i["type"] == 10:
                    if_dict = {
                        "type": i["action"]["type"], "element": i["action"]["element"],
                        "locator": i["action"]["locator"], "locator_select": i["action"]["locator_select"],
                        "page_type": i["action"]["target_type"], "role": i["action"]["input"],
                    }
                    result = element_if(driver, i["name"], browser, result_id, if_dict)
                    if result[0]:
                        if i["children"]:
                            element_for(driver, i["name"], browser, result_id, 1, i["children"], context)
                elif i["type"] == 11:
                    if i["children"]:
                        result = element_for(driver, i["name"], browser, result_id, int(i["action"]["element"]), i["children"], context)
                    else:
                        result = True, f"{i['name']}执行成功"
                elif i["type"] == 12:
                    result = element_wait(driver, i["name"], browser, result_id, i["action"]["element"])
                elif i["type"] == 13:
                    if i["action"]["localstorage"]:
                        set_localstorage(context, i["action"]["localstorage"], browser, result_id)
                    if i["action"]["cookies"]:
                        set_cookie(context, i["action"]["cookies"], browser, result_id, i["action"]["element"])
                    result = element_new_page(context, i["name"], browser, result_id, i["action"]["element"])
                    driver = result[2]
                    context = result[3]
                elif i["type"] == 14:
                    result = element_switch_page(context, i["name"], browser, result_id, "previous", driver)
                    driver = result[2]
                elif i["type"] == 15:
                    result = element_switch_page(context, i["name"], browser, result_id, "next", driver)
                    driver = result[2]
                elif i["type"] == 17:
                    result = element_eval(driver, i["action"]["element"], result_id, browser)
                elif i["type"] == 18:
                    el_status, element = handle_element(driver, i["action"], result_id, browser)
                    if el_status:
                        result = element_upload_file(element, i["name"], browser, result_id, i["action"]["input"])
                if i["action"]["assert"]:
                    status, assert_list = element_assert(driver, browser, result_id, i["action"]["assert"])
                after_img = playwright_screenshot(driver, browser, result_id)
                if result[0]:
                    write_result(i["name"], result[1], browser, result_id, status, before_img, after_img, "", assert_list, menu_id, now_time, "")
                else:
                    write_result(i["name"], result[1], browser, result_id, 0, before_img, after_img, "", assert_list, menu_id, now_time, "")
                after_element_wait(driver, "执行后等待", browser, result_id, i["action"]["after_wait"])
            except Exception as e:
                after_img = ""
                write_result(i["name"], result[1], browser, result_id, 0, before_img, after_img, "", assert_list, menu_id, now_time, "")
        return True, "for循环执行成功", driver, context
    except Exception as e:
        print(f"for_run_script任务执行失败， 原因是：{str(e)}")
        return False, str(e)

def handle_element(driver, action, result_id, browser):
    try:
        if "," in action["element"]:
            element_list = action["element"].split(",")
            for i in element_list:
                action["element"] = i
                write_log(f"正在定位元素：{i}", browser, result_id)
                status, element = locator_action(driver, action, result_id, browser)
                print(status, element)
                if status:
                    return status, element
                write_log(f"识别失败，未找到元素：{i}", browser, result_id)
        else:
            status, element = locator_action(driver, action, result_id, browser)
            return status, element
        return False, f"元素{action['element']}识别失败，未找到元素"
    except Exception as e:
        print(f"handle_element任务执行失败， 原因是：{str(e)}")
        return False, str(e)

def ta_handle_element(driver, action, result_id, browser):
    try:
        if "," in action["element"]:
            element_list = action["element"].split(",")
            for i in element_list:
                action["element"] = i
                status, element = target_locator_action(driver, action, result_id, browser)
                write_log(f"正在定位元素：{i}", browser, result_id)
                if status:
                    return status, element
                write_log(f"识别失败，未找到元素：{i}", browser, result_id)
        else:
            status, element = target_locator_action(driver, action, result_id, browser)
            return status, element
        write_log(f"识别失败，未找到元素：{action['element']}", browser, result_id)
        return False, f"元素{action['element']}识别失败，未找到元素"
    except Exception as e:
        print(f"handle_element任务执行失败， 原因是：{str(e)}")
        return False, str(e)
def locator_action(driver, action, result_id, browser):
    try:
        write_log(f"开始判断元素定位方式", browser, result_id)
        element_value = action["element"]
        if action["locator"] == 1:
            write_log(f"正在使用定位器，开始定位元素：{action['element']}", browser, result_id)
            element = driver.locator(element_value)
        if action["locator"] == 2:
            write_log(f"正在使用选择器，开始定位元素：{action['element']}", browser, result_id)
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
        element.wait_for(state="visible", timeout=action["timeout"] * 1000)
        if element.is_visible():
            return True, element
        return False, f"元素{element_value}识别失败，未找到元素"
    except Exception as e:
        write_log(f"元素定位失败， 原因是：{str(e)}", browser, result_id)
        print(f"locator_action异常：{str(e)}")
        return str(e)

def target_locator_action(driver, action, result_id, browser):
    try:
        write_log(f"开始判断目标元素定位方式", browser, result_id)
        element_value = action["target"]
        if action["target_locator"] == 1:
            write_log(f"正在使用定位器，开始定位目标元素：{action['target']}", browser, result_id)
            element = driver.locator(element_value)
        if action["target_locator"] == 2:
            write_log(f"正在使用选择器，开始定位目标元素：{action['target']}", browser, result_id)
            if action["target_locator_select"] == 1:
                element = driver.locator(f"#{element_value}")
            elif action["target_locator_select"] == 2:
                element = driver.get_by_text(element_value)
            elif action["target_locator_select"] == 3:
                element = driver.get_by_label(element_value)
            elif action["target_locator_select"] == 4:
                element = driver.get_by_title(element_value)
            elif action["target_locator_select"] == 5:
                element = driver.get_by_placeholder(element_value, exact=True)
            elif action["locator_select"] == 6:
                element = driver.get_by_alt_text(element_value)
            elif action["locator_select"] == 7:
                element = driver.get_by_role(action["role"], name=element_value)
        element.wait_for(state="visible", timeout=action["timeout"] * 1000)
        if element.is_visible():
            return True, element
        return element
    except Exception as e:
        write_log(f"目标元素定位失败， 原因是：{str(e)}", browser, result_id)
        print(f"target_locator_action异常：{str(e)}")
        return str(e)

def assert_locator_action(driver, action, result_id, browser):
    try:
        write_log(f"开始判断元素定位方式", browser, result_id)
        element_value = action["element"]
        if action["locator"] == 1:
            write_log(f"正在使用定位器，开始定位元素：{action['element']}", browser, result_id)
            element = driver.locator(element_value)
        if action["locator"] == 2:
            write_log(f"正在使用选择器，开始定位元素：{action['element']}", browser, result_id)
            if action["locator_select"] == 1:
                element = driver.locator(f"#{element_value}")
            elif action["locator_select"] == 2:
                element = driver.get_by_text(text=element_value)
            elif action["locator_select"] == 3:
                element = driver.get_by_label(text=element_value)
            elif action["locator_select"] == 4:
                element = driver.get_by_title(text=element_value)
            elif action["locator_select"] == 5:
                element = driver.get_by_placeholder(text=element_value, exact=True)
            elif action["locator_select"] == 6:
                element = driver.get_by_alt_text(text=element_value)
            elif action["locator_select"] == 7:
                element = driver.get_by_role(role=action["role"], text=element_value)
        return element
    except Exception as e:
        write_log(f"元素定位失败， 原因是：{str(e)}", browser, result_id)
        print(f"assert_locator_action异常：{str(e)}")
        return str(e)

def element_eval(driver, element, result_id, browser):
    try: 
        from playwright.async_api import expect
        write_log(f"正在执行自定义脚本：{element}", browser, result_id)
        eval(element)
        write_log(f"执行自定义脚本成功", browser, result_id)
        return True, f"执行自定义脚本成功: {element}"
    except Exception as e:
        print(f"element_eval异常：{str(e)}")
        write_log(f"执行自定义脚本失败， 原因是：{str(e)}", browser, result_id)
        return False, str(e)

def open_url(browser, action, result_id, context):
    try:
        driver = context.new_page()
        url = action["element"]
        driver.goto(url, wait_until='networkidle')
        result = f"网页打开成功，网页地址：{url}"
        time.sleep(3)
        write_log(result, browser, result_id)
        return True, result, driver
    except Exception as e:
        result = f"网页打开失败，原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result, driver

def set_localstorage(context, localstorage, browser, result_id):
    try:
        result = f"开始设置localStorage"
        write_log(result, browser, result_id)
        for i in localstorage:
            context.add_init_script(script=f"""localStorage.setItem('{i["name"]}', '{i["value"]}');""")
            result = f"localStorage设置成功,  key={i['name']}, value={i['value']}"
            write_log(result, browser, result_id)
        return True
    except Exception as e:
        result = f"localStorage设置失败，原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False
    
def set_cookie(context, cookies, browser, result_id, url):
    try:
        result = f"开始设置cookie"
        parsed_url = urlparse(url)
        write_log(result, browser, result_id)
        for i in cookies:
            i["url"] = f"{parsed_url.scheme}://{parsed_url.netloc}"
        context.add_cookies(cookies)
        for j in cookies:
            result = f"cookie设置成功, key={j['name']}, value={j['value']}"
            write_log(result, browser, result_id)
        return True
    except Exception as e:
        result = f"cookie设置失败，原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False

def element_click(name, browser, result_id, element):
    try:
        element.click()
        write_log(f"元素定位成功， 元素：{element}", browser, result_id)
        result = f"{name}：元素点击成功"
        write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result
    
def element_dblclick(name, browser, result_id, element):
    try:
        element.dblclick()
        write_log(f"元素定位成功， 元素：{element}", browser, result_id)
        result = f"{name}：元素双击成功"
        write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result
    
def element_longclick(driver, name, browser, result_id, element):
    try:
        element.hover()
        driver.mouse.down(button='left')
        driver.wait_for_timeout(2500)
        driver.mouse.up()
        write_log(f"元素定位成功， 元素：{element}", browser, result_id)
        result = f"{name}：元素长按成功"
        write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result

def element_drop(driver, name, browser, result_id, element, target):
    try:
        from_box = element.bounding_box()
        driver.mouse.move(from_box['x'] + from_box['width'] / 2,
                          from_box['y'] + from_box['height'] / 2)
        driver.mouse.down()
        write_log(f"拖拽起始元素定位成功， 元素：{element}", browser, result_id)
        target_box = target.bounding_box()
        driver.mouse.move(target_box['x'] + target_box['width'] / 2,
                          target_box['y'] + target_box['height'] / 2)
        driver.mouse.up()
        write_log(f"拖拽目标元素定位成功， 元素：{target}", browser, result_id)
        result = f"{name}：元素拖拽成功"
        write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result

def element_input(name, browser, result_id, element, input_value):
    try:
        element.fill(input_value)
        write_log(f"元素定位成功， 元素：{element}", browser, result_id)
        result = f"{name}：输入值--{input_value}--成功"
        write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result

def element_add_input(name, browser, result_id, element, input_value):
    try:
        old_text = element.input_value()
        new_text = old_text + input_value
        element.fill(new_text)
        write_log(f"元素定位成功， 元素：{element}", browser, result_id)
        result = f"{name}：补充输入值--{input_value}--成功"
        write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result

def element_input_clear(name, browser, result_id, element):
    try:
        element.fill("")
        write_log(f"元素定位成功， 元素：{element}", browser, result_id)
        result = f"{name}：清空文本--成功"
        write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result

def element_sway_up(driver, name, browser, result_id, action):
    try:
        num = int(action["element"])
        if action["up_type"] == 1:
            driver.mouse.wheel(0, delta_y=-num)
            result = f"{name}：向上滑动像素--{num}--成功"
        else:
            driver.mouse.wheel(0, delta_y=num)
            result = f"{name}：向下滑动像素--{num}--成功"
        time.sleep(3)
        write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result
    
def element_sway_left(driver, name, browser, result_id, action):
    try:
        num = int(action["element"])
        if action["sway_type"] == 1:
            driver.scroll_by(0, num)
            result = f"{name}：向上滑动像素--{num}--成功"
        else:
            driver.scroll_by(0, -num)
            result = f"{name}：向下滑动像素--{num}--成功"
        write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result

def element_if(driver, name, browser, result_id, if_dict):
    try:
        if_list = []
        if_list.append(if_dict)
        assert_result = element_assert(driver, browser, result_id, if_list)
        if assert_result[0] == 1:
            result = f"{name}：判断成功，元素存在"
            write_log(result, browser, result_id)
            return True, result
        else:
            result = f"{name}：判断失败，元素不存在"
            write_log(result, browser, result_id)
            return False, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result

def element_for(driver, name, browser, result_id, num, script, context):
    try:
        for i in range(0, num):
            for_run_script_async(driver, browser, script, result_id, context)
        result = f"{name}：执行成功"
        write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result

def element_wait(driver, name, browser, result_id, wait_time):
    try:
        driver.wait_for_timeout(int(wait_time))
        result = f"{name}：等待--{wait_time}秒--成功"
        write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result
    
def before_element_wait(driver, name, browser, result_id, wait_time):
    try:
        driver.wait_for_timeout(int(wait_time))
        result = f"{name}：执行前等待--{wait_time}秒--成功"
        write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行前等待失败 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result
    
def after_element_wait(driver, name, browser, result_id, wait_time):
    try:
        driver.wait_for_timeout(int(wait_time))
        result = f"{name}：执行后等待--{wait_time}秒--成功"
        write_log(result, browser, result_id)
        return True, result
    except Exception as e:
        result = f"{name}：执行后等待 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result

def element_new_page(context, name, browser, result_id, element):
    try:
        time.sleep(3)
        driver = context.new_page()
        driver.goto(element)
        result = f"{name}：打开新窗口--{element}--成功"
        write_log(result, browser, result_id)
        return True, result, driver, context
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result

def element_switch_page(context, name, browser, result_id, direction , driver):
    try:
        all_pages = context.pages
        for i in all_pages:
            if i.url == driver.url:
                current_index = all_pages.index(i)
        if direction == "next":
        # 切换到下一个标签页
            if current_index < len(all_pages) - 1:
                next_page = all_pages[current_index + 1]
                next_page.bring_to_front()  # 切换到下一个页面
                result = f"切换到下一个标签页，成功"
                write_log(result, browser, result_id)
                return True, result, next_page
            else:
                result = "已经是最后一个标签页，无法向下切换"
                write_log(result, browser, result_id)
                return False, result, driver
        elif direction == "previous":
            # 切换到上一个标签页
            if current_index > 0:
                previous_page = all_pages[current_index - 1]
                previous_page.bring_to_front()  # 切换到上一个页面
                result = f"切换到上一个标签页，成功"
                write_log(result, browser, result_id)
                return True, result, previous_page
            else:
                write_log(result, browser, result_id)
                result = "已经是第一个标签页，无法向下切换"
                return False, result, driver
        else:
            result = "无效的方向，方向应为 'next' 或 'previous'"
        write_log(result, browser, result_id)
        return False, result, driver
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result

def element_upload_file(driver, name, browser, result_id, element):
    try:
        write_log(f"正在执行上传文件文件：{element}", browser, result_id)
        print(f"{project_path}{element}")
        driver.set_input_files(f"{project_path}{element}")
        write_log(f"执行上传文件成功", browser, result_id)
        return True, f"执行上传文件成功"
    except Exception as e:
        result = f"{name}：执行失败 原因是：{str(e)}"
        write_log(result, browser, result_id)
        return False, result

def assert_eval(driver, element, result_id, browser):
    try: 
        from playwright.async_api import expect
        write_log(f"正在执行断言脚本：{element}", browser, result_id)
        eval(element)
        write_log(f"执行自定义断言成功", browser, result_id)
        return True, f"执行断言脚本成功"
    except Exception as e:
        write_log(f"执行断言脚本失败， 原因是：{str(e)}", browser, result_id)
        return False, str(e)

def element_assert(driver, browser, result_id, assert_list):
    status = 1
    for i in assert_list:
        try:
            i["img"] = playwright_screenshot(driver, browser, result_id)
            if i["type"] == 1:
                element = assert_locator_action(driver, i, result_id, browser)
                write_log(f"开始断言元素：{element}， 预期：元素存在", browser, result_id)
                if element.is_visible():
                    result = f"断言成功，元素：{element}--元素存在"
                    i["status"] = 1
                    i["result"] = result
                    write_log(result, browser, result_id)
                else:
                    status = 0
                    result = f"断言失败，元素：{element}--元素不存在"
                    i["status"] = 0
                    i["result"] = result
                    write_log(result, browser, result_id)
            elif i["type"] == 2:
                element = assert_locator_action(driver, i, result_id, browser)
                write_log(f"开始断言元素：{element}， 预期：元素不存在", browser, result_id)
                if element.is_visible():
                    status = 0
                    result = f"断言失败，元素：{element}--元素存在"
                    i["status"] = 0
                    i["result"] = result
                    write_log(result, browser, result_id)
                else:
                    result = f"断言成功，元素：{element}--元素不存在"
                    i["status"] = 1
                    i["result"] = result
                    write_log(result, browser, result_id)
            elif i["type"] == 3:
                element = driver.content()
                write_log(f"开始断言文本：{element}， 预期：文本存在", browser, result_id)
                if i["element"] in element:
                    result = f"断言成功，文本：{element}--文本存在"
                    i["status"] = 1
                    i["result"] = result
                    write_log(result, browser, result_id)
                else:
                    status = 0
                    result = f"断言失败，文本：{element}--文本不存在"
                    i["status"] = 0
                    i["result"] = result
                    write_log(result, browser, result_id)
            elif i["type"] == 4:
                element = driver.content()
                write_log(f"开始断言文本：{element}， 预期：文本不存在", browser, result_id)
                if i["element"] in element:
                    status = 0
                    result = f"断言失败，文本：{element}--文本存在"
                    i["status"] = 0
                    i["result"] = result
                    write_log(result, browser, result_id)
                else:
                    result = f"断言成功，文本：{element}--文本不存在"
                    i["status"] = 1
                    i["result"] = result
                    write_log(result, browser, result_id)
            elif i["type"] == 5:
                title = driver.title()
                url = driver.url
                if i["page_type"] == 2:
                    write_log(f"开始断言网页标题：{title}， 预期：标题一致", browser, result_id)
                    if title == i["element"]:
                        result = f"断言成功，网页标题：{title}--标题一致"
                        i["status"] = 1
                        i["result"] = result
                        write_log(result, browser, result_id)
                    else:
                        status = 0
                        result = f"断言失败，网页标题：{title}，预期：{i['element']}--标题不一致"
                        i["status"] = 0
                        i["result"] = result
                        write_log(result, browser, result_id)
                elif i["page_type"] == 1:
                    write_log(f"开始断言网址：{url}， 预期：网址一致", browser, result_id)
                    if url == i["element"]:
                        result = f"断言成功，网址：{url}--网址一致"
                        i["status"] = 1
                        i["result"] = result
                        write_log(result, browser, result_id)
                    else:
                        status = 0
                        result = f"断言失败，网址：{url}，预期：{i['element']}--网址不一致"
                        i["status"] = 0
                        i["result"] = result
                        write_log(result, browser, result_id)
            elif i["type"] == 6:
                write_log(f"开始执行自定义脚本断言：{i['element']}", browser, result_id)
                result = assert_eval(driver, i["element"], result_id, browser)
                if result[0]:
                    i["status"] = 1
                    i["result"] = f"断言成功，自定义脚本断言：{i['element']}--断言成功"
                    write_log(i["result"], browser, result_id)
                else:
                    status = 0
                    i["status"] = 0
                    i["result"] = f"断言失败，自定义脚本断言：{i['element']}--断言失败"
                    write_log(result, browser, result_id)
        except Exception as e:
            status = 0
            i["status"] = 0
            i["result"] = f"断言失败，原因是：{str(e)}"
            write_log(i["result"], browser, result_id)
    return status, assert_list

def playwright_screenshot(driver, browser, result_id):
    try:
        BASE_APP_DIR = Path(f"{playwright_result_path}/{result_id}/{browser}")
        if not BASE_APP_DIR.exists():
            os.makedirs(BASE_APP_DIR)
        new_filename = '{}_{}_{}'.format(browser, datetime.now().strftime('%Y%m%d%H%M%S%f'), "web.png")
        path = BASE_APP_DIR / new_filename
        driver.screenshot(path=path)
        return f"/media/playwright/{result_id}/{browser}/{new_filename}"
    except Exception as e:
        print(f"截图失败， 原因是：{str(e)}")

def write_log(result, browser, result_id):
    try:
        BASE_APP_DIR = Path(f"{playwright_result_path}/{result_id}/{browser}")
        if not BASE_APP_DIR.exists():
            os.makedirs(BASE_APP_DIR)
        path = BASE_APP_DIR / f"{browser}_result.txt"
        with open(path, "a") as file:
            file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {result} \n")
    except Exception as e:
        print(f"结果写入文件失败， 原因是：{str(e)}")

def write_result(name, log, browser, result_id, status, before_img, after_img, video, assert_result, menu_id, now_time, trace):
    try:
        pass
        # asyncio.run(Web_result_detail.create(
        #     name=name, result_id=result_id, browser=browser,
        #     log=log, status=status, before_img=before_img,
        #     after_img=after_img, video=video, assert_result=assert_result, menu_id=menu_id,
        #     create_time=now_time, trace=trace
        # ))
    except Exception as e:
        print(name, log, browser, result_id, status, before_img, after_img, video, assert_result, menu_id, trace)
        print(f"write_result异常：{str(e)}")

def run_end(result_id, browser):
    try:
        run_false = 0
        detail = asyncio.run(Web_result_detail.filter(result_id=result_id, browser=browser))
        total = len(detail) - 1
        for i in detail:
            if i.status == 0:
                run_false += 1
        run_true = total - run_false
        result = {
            "browser": browser,
            "total": total,
            "run_true": run_true,
            "run_false": run_false
        }
        data = asyncio.run(Web_result_list.filter(result_id=result_id).first().values())
        data["result"].append(result)
        asyncio.run(Web_result_list.filter(result_id=result_id).update(result=data["result"], end_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    except Exception as e:
        print(f"run_end异常：{str(e)}")

def parse_timestamp(line):
    # 解析时间戳
    try:
        # 提取每行开头的时间戳部分
        timestamp_str = line.split(' ')[0] + ' ' + line.split(' ')[1]
        return True, int(datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S').timestamp())
    except Exception as e:
        # 如果某一行没有时间戳或格式不正确，返回 None
        return False, e

def filter_by_time_range(lines, start_time, end_time):
    # 根据时间范围筛选内容
    start = int(datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').timestamp())
    end = int(datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').timestamp())
    filtered_lines = []
    for line in lines:
        status, log_time = parse_timestamp(line)
        if status:
            if start <= log_time <= end:
                filtered_lines.append(line)
    return filtered_lines
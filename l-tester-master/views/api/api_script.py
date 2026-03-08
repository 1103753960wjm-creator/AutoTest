from datetime import datetime
import time
import uuid
from pathlib import Path
import os
from views.api.api_common import (
    after_set_var,
    after_wait_time,
    local_db_assert,
    pre_request_api,
    pre_set_var,
    pre_wait_time,
    res_assert,
    send_api_request,
)
from views.api.api_model import (
    Api,
    Api_menu,
    Api_params,
    Api_script_result,
    Api_script_result_list,
)
from views.api.common import handle_var, params_header, url_host
from config.settings import api_result_path
from views.warning_call.call_commom import send_notice


async def handle_result_id():
    try:
        # 生成一个随机的 UUID
        random_uuid = uuid.uuid4()
        return str(random_uuid)
    except Exception as e:
        return str(e)


async def handle_api_script(data):
    try:
        result_id = data["result_id"]
        env_id = data["config"]["env_id"]
        all_pass = 0
        all_fail = 0
        total = 0
        for i in data["run_list"]:
            i["status"] = 1
            i["pass"] = 0
            i["fail"] = 0
            i["uuid"] = await handle_result_id()
            if "params_id" in i["config"] and i["config"]["params_id"] is not None:
                params_id = i["config"]["params_id"]
            else:
                params_id = None
            for j in i["script"]:
                total = total + len(i["script"])
                j["uuid"] = await handle_result_id()
                await write_log(i["uuid"], result_id, f"开始执行接口-{j['name']}")
                status, api_req, api_res = await handle_api_request(
                    j, result_id, i["uuid"], env_id, params_id
                )
                if status:
                    i["pass"] = i["pass"] + 1
                    all_pass = all_pass + 1
                    await Api_script_result.create(
                        name=j["name"],
                        req=api_req,
                        res=api_res,
                        result_id=result_id,
                        status=1,
                        uuid=j["uuid"],
                        menu_id=i["uuid"],
                    )
                else:
                    i["status"] = 0
                    i["fail"] = i["fail"] + 1
                    all_fail = all_fail + 1
                    await Api_script_result.create(
                        name=j["name"],
                        req=api_req,
                        res=api_res,
                        result_id=result_id,
                        status=0,
                        uuid=j["uuid"],
                        menu_id=i["uuid"],
                    )
                await write_log(i["uuid"], result_id, f"接口-{j['name']}执行完成")
                time.sleep(3)
        percent = round(all_pass / total * 100, 2)
        await Api_script_result_list.filter(result_id=result_id).update(
            end_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            script=data["run_list"],
            result={
                "total": total,
                "pass": all_pass,
                "fail": all_fail,
                "percent": percent,
            },
        )
        await Api_script_result.create(
            name="执行结束", req={}, res={}, result_id=result_id, status=1, menu_id=""
        )
        notice_data = {
            "task_name": data["name"],
            "result_id": result_id,
            "total": total,
            "passed": all_pass,
            "fail": all_fail,
            "un_run": total - all_pass - all_fail,
            "percent": percent,
        }
        await send_notice(33, "api_report", notice_data)
        print(f"接口执行完成，结果：{all_pass}通过，{all_fail}失败")
    except Exception as e:
        print(f"函数：handle_api_script---异常，原因是{str(e)}")


async def handle_api_request(data, result_id, uuid, env_id, params_id):
    req = {}
    try:
        api_id = data["api_id"]
        api_value = await Api.filter(id=api_id).first().values()
        api = api_value["req"]
        url = await handle_url(uuid, result_id, env_id, api_value["url"])
        header = (
            {}
            if not api["header"]
            else await handle_params(uuid, result_id, env_id, api["header"], "header")
        )
        params = (
            {}
            if not api["params"]
            else await handle_params(uuid, result_id, env_id, api["params"], "params")
        )
        if (
            "params_id" in api.keys()
            and api["params_id"] is not None
            and params_id is not None
        ):
            params_value = await Api_params.filter(id=params_id).first().values()
            api["body"].update(params_value["value"])
        body = await handle_body(uuid, result_id, env_id, api["body"])
        form_data = (
            {}
            if not api["form_data"]
            else await handle_params(
                uuid, result_id, env_id, api["form_data"], "form_data"
            )
        )
        form_urlencoded = (
            {}
            if not api["form_urlencoded"]
            else await handle_params(
                uuid, result_id, env_id, api["form_urlencoded"], "form_urlencoded"
            )
        )
        file = api["file_path"]
        config = api["config"]
        before_status, before = (
            (True, [])
            if not api["before"]
            else await handle_before(uuid, result_id, env_id, api["before"])
        )
        res = await send_api_request(
            api["method"],
            url,
            header,
            params,
            api["body_type"],
            body,
            form_data,
            form_urlencoded,
            file,
            config,
        )
        await write_log(uuid, result_id, f"请求结果：{res['body']}")
        after_status, after = (
            (True, [])
            if not api["after"]
            else await handle_after(
                uuid, result_id, env_id, api["after"], res, header, body
            )
        )
        assert_status, assert_res = (
            (True, [])
            if not api["assert"]
            else await handle_assert(
                uuid, result_id, env_id, api["assert"], res, header, body
            )
        )
        if (
            not before_status
            or not after_status
            or not assert_status
            or res["code"] != 200
        ):
            res_status = False
        else:
            res_status = True
        req = {
            "params_id": params_id,
            "method": api["method"],
            "body_type": api["body_type"],
            "url": url,
            "header": (
                []
                if not header
                else [{"key": k, "value": v, "status": True} for k, v in header.items()]
            ),
            "params": (
                []
                if not header
                else [{"key": k, "value": v, "status": True} for k, v in params.items()]
            ),
            "body": body,
            "form_data": (
                []
                if not header
                else [
                    {"key": k, "value": v, "status": True} for k, v in form_data.items()
                ]
            ),
            "form_urlencoded": (
                []
                if not header
                else [
                    {"key": k, "value": v, "status": True}
                    for k, v in form_urlencoded.items()
                ]
            ),
            "file_path": file,
            "assert": api["assert"],
            "before": api["before"],
            "config": config,
            "assert": api["assert"],
            "after": api["after"],
        }
        res["before"] = before
        res["after"] = after
        res["assert"] = assert_res
        return res_status, req, res
    except Exception as e:
        await write_log(uuid, result_id, f"构建请求失败，原因：{str(e)}")
        return (
            False,
            req,
            {
                "status": 0,
                "message": f"请求接口失败， 原因是：{str(e)}",
                "code": 500,
                "body": {"msg": "接口请求失败", "exception": str(e)},
                "header": {},
                "size": 0,
                "res_time": 0,
            },
        )


async def handle_url(uuid, result_id, env_id, url):
    try:
        api_url = await url_host(env_id, url)
        result = f"请求地址-url：{api_url}"
        await write_log(uuid, result_id, result)
        return api_url
    except Exception as e:
        await write_log(uuid, result_id, f"请求url地址解析失败，原因是：{e}")
        return str(e)


async def handle_params(uuid, result_id, env_id, params, type):
    try:
        params_value = await params_header(params)
        params_res = await handle_var(env_id, params_value)
        await write_log(uuid, result_id, f"请求参数-{type}：{params_res}")
        return params_res
    except Exception as e:
        await write_log(uuid, result_id, f"请求参数解析失败，原因：{str(e)}")
        return {"Exception": str(e)}


async def handle_body(uuid, result_id, env_id, body):
    try:
        body_res = await handle_var(env_id, body)
        await write_log(uuid, result_id, f"请求体-body：{body_res}")
        return body_res
    except Exception as e:
        await write_log(uuid, result_id, f"请求体解析失败，原因：{str(e)}")
        return {"Exception": str(e)}


async def handle_before(uuid, result_id, env_id, before):
    try:
        res_status = True
        result = []
        for i in before:
            if i["type"] == 1:
                api_id = (
                    await Api_menu.filter(id=i["api_id"][-1], type=3).first().values()
                )
                if api_id:
                    api = await Api.filter(id=api_id["api_id"]).first().values()
                    res = await pre_request_api(api, i["env_id"])
                else:
                    res = {
                        "status": 0,
                        "message": f"前置操作-预请求接口：未选择接口用例，请求失败",
                        "content": [],
                    }
            elif i["type"] == 2:
                res = await pre_set_var(i, env_id)
            elif i["type"] == 3:
                res = await pre_wait_time(i["wait_time"])
            if res["status"] == 0:
                res_status = False
                await write_log(uuid, result_id, res["message"])
            else:
                await write_log(uuid, result_id, res["message"])
            res["type"] = i["type"]
            result.append(res)
        return res_status, result
    except Exception as e:
        await write_log(uuid, result_id, f"前置操作解析失败，原因：{str(e)}")
        return False, [{"status": 0, "message": "前置操作执行失败，原因：" + str(e)}]


async def handle_after(uuid, result_id, env_id, after, res, header, body):
    try:
        res_status = True
        result = []
        for i in after:
            if i["type"] == 1:
                res = await after_set_var(i, res, header, body, env_id)
            elif i["type"] == 2:
                res = await after_wait_time(i["wait_time"])
            if res["status"] == 0:
                res_status = False
                await write_log(uuid, result_id, res["message"])
            else:
                await write_log(uuid, result_id, res["message"])
            res["type"] = i["type"]
            result.append(res)
        return res_status, result
    except Exception as e:
        await write_log(uuid, result_id, f"后置操作解析失败，原因：{str(e)}")
        return False, [{"status": 0, "message": "后置操作执行失败，原因：" + str(e)}]


async def handle_assert(uuid, result_id, env_id, assert_data, res, header, body):
    try:
        res_status = True
        result = []
        for i in assert_data:
            assert_res = {}
            if i["type"] == 1:
                assert_res = await res_assert(i, res, header, body)
                if assert_res["status"] == 0:
                    res_status = False
                await write_log(uuid, result_id, assert_res["message"])
            elif i["type"] == 4:
                assert_res = {
                    "status": 1,
                    "message": f"直连-数据库断言-全部成功",
                    "content": [],
                }
                assert_res["content"] = await local_db_assert(i, res, header, body)
                for j in assert_res["content"]:
                    if j["status"] == 0:
                        res_status = False
                        await write_log(uuid, result_id, j["message"])
                        assert_res["status"] = 0
                        assert_res["message"] = f"直连-数据库断言执行完成，断言出现错误"
            assert_res["type"] = i["type"]
            result.append(assert_res)
        return res_status, result
    except Exception as e:
        await write_log(uuid, result_id, f"断言操作解析失败，原因：{str(e)}")
        return False, [{"status": 0, "message": "断言操作执行失败，原因：" + str(e)}]


async def write_log(uuid, result_id, result):
    try:
        BASE_APP_DIR = Path(f"{api_result_path}/{result_id}")
        if not BASE_APP_DIR.exists():
            os.makedirs(BASE_APP_DIR)
        path = BASE_APP_DIR / f"{uuid}.txt"
        res_path = BASE_APP_DIR / f"{result_id}.txt"
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(res_path, "a") as file:
            file.write(f"{time} {result} \n")
        with open(path, "a") as file:
            file.write(f"{time} {result} \n")
    except Exception as e:
        print(f"结果写入文件失败， 原因是：{str(e)}")

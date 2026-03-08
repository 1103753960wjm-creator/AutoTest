from datetime import datetime
import json
import time
from urllib.parse import urlparse
import pymysql
import requests
from config.settings import project_path
from views.api.api_model import Api, Api_db, Api_envs, Api_menu, Api_params, Api_result, Api_service, Api_var
from views.api.common import handle_var, params_header
import jsonpath
# 发送请求
async def handle_api_request(data):
    try:
        before = []
        after = []
        assert_res = []
        env_id = data["env_id"]
        url = await handle_var(env_id, data["url"])
        params_id = None
        if "params_id" in data["req"] and data["req"]["params_id"] != None:
            params_id = data["req"]["params_id"]
            params_value = await Api_params.filter(id=data["req"]["params_id"]).first().values()
            data["req"]["body"].update(params_value["value"])
        body = await handle_var(env_id, data["req"]["body"])
        method = data["req"]["method"]
        body_type = data["req"]["body_type"]
        headers = {} if not data["req"]["header"] else await params_header(data["req"]["header"])
        headers = await handle_var(env_id, headers)
        params = {} if not data["req"]["params"] else await params_header(data["req"]["params"])
        params = await handle_var(env_id, params)
        form_data = {} if not data["req"]["form_data"] else await params_header(data["req"]["form_data"])
        form_data = await handle_var(env_id, form_data)
        form_urlencoded = {} if not data["req"]["form_urlencoded"] else await params_header(data["req"]["form_urlencoded"])
        form_urlencoded = await handle_var(env_id, form_urlencoded)
        file = data["req"]["file_path"]
        config = data["req"]["config"]
        if data["req"]["before"]:
            before = await pre_request(data["req"]["before"], env_id)
        res = await send_api_request(method, url, headers, params, body_type, body, form_data, form_urlencoded, file, config)
        if data["req"]["after"]:
            after = await after_request(data["req"]["after"], res, headers, body, env_id)
        if data["req"]["assert"]:
            assert_res = await handle_assert(data["req"]["assert"], res, headers, body)
        res["before"] = before
        res["after"] = after
        res["assert"] = assert_res
        res["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await Api_result.create(
            req={
                "url": url, "body": data["req"]["body"], "params": data["req"]["params"], "header": data["req"]["header"], "form_data": data["req"]["form_data"],
                "file_path": data["req"]["file_path"], "form_urlencoded": data["req"]["form_urlencoded"], "config": config, "body_type": body_type,
                "method": method, "before": data["req"]["before"], "after": data["req"]["after"], "assert": data["req"]["assert"], "params_id": params_id
            }, res=res, user_id=data["user_id"], api_id=data["id"]
        )
        return res
    except Exception as e:
        print("send_api_request函数执行失败，原因：", e)
        return {
            "code": 500,
            "before": [],
            "after": [],
            "assert": [],
            "res_time": 0,
            "body": {
                "code": 500,
                "msg": "send_api_request函数执行失败，原因：" + str(e)
            },
            "header": {}
        }

# 处理预请求操作
async def pre_request(data, env_id):
    try:
        result = []
        for i in data:
            if i["type"] == 1:
                api_id = await Api_menu.filter(id=i["api_id"][-1], type=3).first().values()
                if api_id:
                    api = await Api.filter(id=api_id["api_id"]).first().values()
                    res = await pre_request_api(api, i["env_id"])
                else:
                    res = {
                        "status": 0,
                        "message": f"前置操作-预请求接口：未选择接口用例，请求失败",
                        "content": []
                    }
            elif i["type"] == 2:
                res = await pre_set_var(i, env_id)
            elif i["type"] == 3:
                res = await pre_wait_time(i["wait_time"])
            res["type"] = i["type"]
            result.append(res)
        return result
    except Exception as e:
        return [{"status": 0, "message": "前置操作执行失败，原因：" + str(e)}]
       
# 前置操作-预请求接口
async def pre_request_api(data, env_id):
    try:
        url = await handle_var(env_id, data["url"])
        body = await handle_var(env_id, data["req"]["body"])
        method = data["req"]["method"]
        body_type = data["req"]["body_type"]
        headers = {} if not data["req"]["header"] else await params_header(data["req"]["header"])
        headers = await handle_var(env_id, headers)
        params = {} if not data["req"]["params"] else await params_header(data["req"]["params"])
        params = await handle_var(env_id, params)
        form_data = {} if not data["req"]["form_data"] else await params_header(data["req"]["form_data"])
        form_data = await handle_var(env_id, form_data)
        form_urlencoded = {} if not data["req"]["form_urlencoded"] else await params_header(data["req"]["form_urlencoded"])
        form_urlencoded = await handle_var(env_id, form_urlencoded)
        file = data["req"]["file_path"]
        config = data["req"]["config"]
        res = await send_api_request(method, url, headers, params, body_type, body, form_data, form_urlencoded, file, config)
        if data["req"]["after"]:
            after = await after_request(data["req"]["after"], res, headers, body, env_id)
        if data["req"]["assert"]:
            assert_res = await handle_assert(data["req"]["assert"], res, headers, body)
        res["before"] = []
        res["after"] = after
        res["assert"] = assert_res
        res["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if res["code"] == 200:
            result = {
                "status": 1,
                "message": f"前置操作-预请求接口：{url} 成功",
                "content": res
            }
        else:
            result = {
                "status": 0,
                "message": f"前置操作-预请求接口：{url} 失败",
                "content": res
            }
        return result
    except Exception as e:
        result = {
                "status": 0,
                "message": f"前置操作-预请求接口：{url} 失败， 原因是：{str(e)}",
                "content": res
            }
        return result
    
# 前置操作-设置环境变量
async def pre_set_var(data, env_id):
   try:
        found = False
        if data["env_type"] == 1:
            env = await Api_envs.filter(id=env_id).first().values()
            for i in env["variable"]:
                if data["name"] == i["name"]:
                   i["value"] = data["value"]
                   found = True
                   break
            if found:
                await Api_envs.filter(id=env_id).update(variable=env["variable"])
            else:
                env["variable"].append({
                       "name": data["name"],
                       "value": data["value"]
                   })
                await Api_envs.filter(id=env_id).update(variable=env["variable"])
            message = f"前置操作-设置环境变量：{data['name']} 成功"
        elif data["env_type"] == 2:
            if await Api_var.filter(id=env_id, name=data['name']).exists():
               await Api_var.filter(id=env_id, name=data['name']).update(value=data["value"])
            else:
               await Api_var.create(name=data["name"], value=data["value"])
            message = f"前置操作-设置全局变量：{data['name']} 成功"
        return {
            "status": 1,
            "message": message
        }
   except Exception as e:
       return {
           "status": 0,
           "message": f"前置操作-设置变量：{data['name']} 失败，原因：{str(e)}"
       }

# 前置操作-等待时长
async def pre_wait_time(wait_time):
    try:
        time.sleep(wait_time)
        res = {
            "status": 1,
            "message": f"前置操作-等待时长：{wait_time} 秒 成功"
        }
        return res
    except Exception as e:
        res = {
            "status": 0,
            "message": f"前置操作-等待时长：{wait_time} 秒 失败，原因是：{str(e)}"
        }
        return res

# 处理后置操作
async def after_request(data, res, header, body, env_id):
    try:
        result = []
        for i in data:
            if i["type"] == 1:
                after_res = await after_set_var(i, res, header, body, env_id)
            elif i["type"] == 2:
                after_res = await after_wait_time(i["wait_time"])
            result.append(after_res)
        return result
    except Exception as e:
        return [{"status": 0, "message": "后置操作执行失败，原因：" + str(e)}]
    
# 后置操作-提取变量
async def after_set_var(data, res, header, body, env_id):
    try:
        res_status, res_data = await jsonpath_value(data, res, header, body)
        found = False
        if data["env_type"] == 1:
            env = await Api_envs.filter(id=env_id).first().values()
            for i in env["variable"]:
                if data["value"] == i["name"]:
                   i["value"] = res_data
                   found = True
                   break
            if found:
                await Api_envs.filter(id=env_id).update(variable=env["variable"])
            else:
                env["variable"].append({
                       "name": data["value"],
                       "value": res_data
                   })
                await Api_envs.filter(id=env_id).update(variable=env["variable"])
        elif data["env_type"] == 2:
            if await Api_var.filter(id=env_id, name=data["value"]).exists():
               await Api_var.filter(id=env_id, name=data["value"]).update(value=res_data)
            else:
               await Api_var.create(name=data["value"], value=res_data)
        if res_status:
            return {
                "status": 1,
                "message": f"后置操作-提取目标值：{data['name']}={res_data} ，赋值给 {data['value']} 成功"
            }
        else:
            return {
                "status": 0,
                "message": f"后置操作-提取目标值：{data['name']}={res_data} ，赋值给 {data['value']}失败，原因是：{res_data}"
            }
    except Exception as e:
        return {
           "status": 0,
           "message": f"后置操作-设置变量：{data['name']} 失败，原因：{str(e)}"
       }
    
# 后置操作-等待时长
async def after_wait_time(wait_time):
    try:
        time.sleep(wait_time)
        res = {
            "status": 1,
            "message": f"后置操作-等待时长：{wait_time} 秒 成功"
        }
        return res
    except Exception as e:
        res = {
            "status": 0,
            "message": f"后置操作-等待时长：{wait_time} 秒 失败，原因是：{str(e)}"
        }
        return res

# jsonpath获取目标值
async def jsonpath_value(data, res, header, body):
    try:
        if data["res_type"] == 1:
            json_data = res["body"]
        elif data["res_type"] == 2:
            json_data = header
        elif data["res_type"] == 3:
            json_data = body
        elif data["res_type"] == 4:
            print(data)
            json_data = res["header"]
        res_data = jsonpath.jsonpath(json_data, data["name"])[0]
        return True, str(res_data)
    except Exception as e:
        return False, f"获取断言目标值失败，原因：{str(e)}"

# 处理断言
async def handle_assert(data, res, header, body):
    try:
        result = []
        for i in data:
            assert_res = {}
            if i["type"] == 1:
                assert_res = await res_assert(i, res, header, body)
            elif i["type"] == 4:
                assert_res = {
                    "status": 1,
                    "message": f"直连-数据库断言-全部成功",
                    "content": []
                }
                assert_res["content"] = await local_db_assert(i, res, header, body)
                for j in assert_res["content"]:
                    if j["status"] == 0:
                        assert_res["status"] = 0
                        assert_res["message"] = f"直连-数据库断言执行完成，断言出现错误"    
            assert_res["type"] = i["type"]
            result.append(assert_res)
        return result
    except Exception as e:
        return [{"status": 0, "message": "断言操作执行失败，原因：" + str(e)}]

# 响应结果断言
async def res_assert(data, res, header, body):
    try:
        res_status, res_data = await jsonpath_value(data, res, header, body)
        if res_status:
            if data["value"] == res_data:
                return {
                    "status": 1,
                    "message": f"断言 {data['name']} = {data['value']} 成功"
                }
            else:
                return {
                    "status": 0,
                    "message": f"断言 {data['name']} = {data['value']} 失败，实际值为：{res_data}"
                }
        else:
            return {
                "status": 0,
                "message": f"断言 {data['name']} = {data['value']} 失败，原因是：{res_data}"
            }
    except Exception as e:
        return {
           "status": 0,
           "message": f"断言 {data['name']} = {data['value']} 失败，原因：{str(e)}"
       }


async def db_assert(data, res, header, body, assert_data):
    try:
        if data["type"] == 1:
            json_data = res["body"]
            res_data = jsonpath.jsonpath(json_data, data["value"])[0]
        elif data["type"] == 2:
            json_data = header
            res_data = jsonpath.jsonpath(json_data, data["value"])[0]
        elif data["type"] == 3:
            json_data = body
            res_data = jsonpath.jsonpath(json_data, data["value"])[0]
        elif data["type"] == 4:
            json_data = res["header"]
            res_data = jsonpath.jsonpath(json_data, data["value"])[0]
        elif data["type"] == 5:
            res_data =  data["value"]
        data["assert_value"] = str(assert_data[data["name"]])
        res = await db_result_assert(data, res_data)
        return res
    except Exception as e:
        return {
            "status": 0,
            "message": f"获取断言目标值失败，原因：{str(e)}"
        }

async def db_result_assert(data, res_data):
    try:
        if data["assert_value"] == res_data:
            return {
                "status": 1,
                "message": f"断言 {data['name']} = {data['value']} 成功"
            }
        else:
            return {
                "status": 0,
                "message": f"断言 {data['name']} = {data['value']} 失败，实际值为：{data['name']}={data['assert_value']}, {data['value']}={res_data}"
            }
    except Exception as e:
        return {
           "status": 0,
           "message": f"断言 {data['name']} = {data['value']} 失败，原因：{str(e)}"
       }

# 直连数据库查询
async def local_db_execute(local_db_id, local_db_table, local_db_where):
    try:
        api_db = await Api_db.filter(id=local_db_id).first().values()
        db = api_db["config"]
        conn = pymysql.connect(host=db["host"],
                                   user=db["user"], passwd=db["password"],
                                   db=db["database"], port=int(db["port"]))
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {local_db_table} where {local_db_where} limit 1")
        result = [dict(zip([column[0] for column in cur.description], row)) for row in cur.fetchall()]
        return result[0]
    except Exception as e:
        return f"查询数据库失败，原因是：{str(e)}"

# 直连数据库断言
async def local_db_assert(data, res, header, body):
    try:
        result = []
        db_res = await local_db_execute(data["local_db"], data["local_db_table"], data["local_db_where"])
        for i in data["local_db_assert"]:
            assert_res = await db_assert(i, res, header, body, db_res)
            result.append(assert_res)
        return result
    except Exception as e:
        return [{"status": 0, "message": "直连-数据库断言操作执行失败，原因：" + str(e)}]

async def send_api_request(method, url, headers, params, body_type, body, form_data, form_urlencoded, file, config):
    try:
        if method == 1:
            res = await send_get_request(url, headers, params, config)
        elif method == 2:
            if body_type == 1:
                res = await send_post_json(url, headers, {}, config)
            elif body_type == 2:
                res = await send_post_json(url, headers, body, config)
            elif body_type == 3:
                res = send_post_data(url, headers, form_data, config)
            elif body_type == 4:
                res = await send_post_data(url, headers, form_urlencoded, config)
            elif body_type == 5:
                res = await send_post_file(url, file, config)
        elif method == 3:
            res = await send_put_request(url, headers, params, body, config)
        elif method == 4:
            res = await send_delete_request(url, headers, params, config)
        elif method == 5:
            pass
        return res
    except Exception as e:
        print("send_api_request函数执行失败，原因：", e)
        return str(e)

async def send_get_request(url, headers, params, config):
    try:
        print("params", params)
        res = requests.get(url, headers=headers, params=params, timeout=(config["req_timeout"], config["res_timeout"]))
        return {
            "code": res.status_code,
            "res_time": str(round(res.elapsed.total_seconds() * 1000, 2)),
            "body": json.loads(res.text),
            "header": dict(res.headers),
            "size": str(res.text.__sizeof__() + res.headers.__sizeof__())
        }
    except Exception as e:
        print("send_get_request函数执行失败，原因：", e)
        return {
            "code": 500,
            "body": {
                "msg": "接口请求失败",
                "exception": str(e)
            },
            "header": {},
            "size": 0,
            "res_time": 0
        }

async def send_post_json(url, headers, body, config):
    try:
        res = requests.post(url=url, headers=headers, json=body, timeout=(config["req_timeout"], config["res_timeout"]))
        return {
            "code": res.status_code,
            "res_time": str(round(res.elapsed.total_seconds() * 1000, 2)),
            "body": json.loads(res.text),
            "header": dict(res.headers),
            "size": str(res.text.__sizeof__() + res.headers.__sizeof__())
        }
    except Exception as e:
        print("send_post_request函数执行失败，原因：", e)
        return {
            "code": 500,
            "body": {
                "msg": "接口请求失败",
                "exception": str(e)
            },
            "header": {},
            "size": 0,
            "res_time": 0
        }

async def send_post_data(url, headers, body, config):
    try:
        res = requests.post(url=url, headers=headers, data=body, timeout=(config["req_timeout"], config["res_timeout"]))
        return {
            "code": res.status_code,
            "res_time": str(round(res.elapsed.total_seconds() * 1000, 2)),
            "body": json.loads(res.text),
            "header": dict(res.headers),
            "size": str(res.text.__sizeof__() + res.headers.__sizeof__())
        }
    except Exception as e:
        print("send_post_request函数执行失败，原因：", e)
        return {
            "code": 500,
            "body": {
                "msg": "接口请求失败",
                "exception": str(e)
            },
            "header": {},
            "size": 0,
            "res_time": 0
        }

async def send_post_file(url, file, config):
    try:
        files = []
        for i in file:
            file_path = f"{project_path}{i}"
            file_name = i.split("/")[-1]
            files.append(
                ('file',(file_name, open(file_path,'rb'), 'text/plain'))
            )
        res = requests.request("POST", url=url, files=files, data={}, timeout=(config["req_timeout"], config["res_timeout"]))
        return {
            "code": res.status_code,
            "res_time": str(round(res.elapsed.total_seconds() * 1000, 2)),
            "body": json.loads(res.text),
            "header": dict(res.headers),
            "size": str(res.text.__sizeof__() + res.headers.__sizeof__())
        }
    except Exception as e:
        print("send_post_request函数执行失败，原因：", e)
        return {
            "code": 500,
            "body": {
                "msg": "接口请求失败",
                "exception": str(e)
            },
            "header": {},
            "size": 0,
            "res_time": 0
        }

async def send_put_request(url, headers, params, body, config):
    try:
        res = requests.put(url, headers=headers, params=params, json=body, timeout=(config["req_timeout"], config["res_timeout"]))
        return {
            "code": res.status_code,
            "res_time": str(round(res.elapsed.total_seconds() * 1000, 2)),
            "body": json.loads(res.text),
            "header": dict(res.headers),
            "size": str(res.text.__sizeof__() + res.headers.__sizeof__())
        }
    except Exception as e:
        print("send_put_request函数执行失败，原因：", e)
        return {
            "code": 500,
            "body": {
                "msg": "接口请求失败",
                "exception": str(e)
            },
            "header": {},
            "size": 0,
            "res_time": 0
        }

async def send_delete_request(url, headers, params, config):
    try:
        res = requests.delete(url, headers=headers, params=params, timeout=(config["req_timeout"], config["res_timeout"]))
        return {
            "code": res.status_code,
            "res_time": str(round(res.elapsed.total_seconds() * 1000, 2)),
            "body": json.loads(res.text),
            "header": dict(res.headers),
            "size": str(res.text.__sizeof__() + res.headers.__sizeof__())
        }
    except Exception as e:
        print("send_delete_request函数执行失败，原因：", e)
        return {
            "code": 500,
            "body": {
                "msg": "接口请求失败",
                "exception": str(e)
            },
            "header": {},
            "size": 0,
            "res_time": 0
        }
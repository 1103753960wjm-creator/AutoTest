from datetime import datetime
import json
from views.api.api_model import Api, Api_menu, Api_service, Api_update


async def handle_gitlab(data, service_id, user_id):
    try:
        service = await Api_service.filter(id=service_id).first().values()
        service_name = "{{" + service["name"] + "}}"
        await Api_menu.filter(api_service=service_id, type=2).update(status=0)
        update_num = 0
        create_num = 0
        for i in data:
            if i["isFolder"] == 1:
                if await Api_menu.filter(
                    name=i["name"], api_service_id=service_id
                ).exists():
                    first_menu = (
                        await Api_menu.filter(name=i["name"], api_service_id=service_id)
                        .first()
                        .values()
                    )
                    first_id = first_menu["id"]
                else:
                    first_menu = await Api_menu.create(
                        name=i["name"],
                        type=0,
                        pid=0,
                        user_id=user_id,
                        api_service_id=service_id,
                        status=1,
                    )
                    first_id = first_menu.id
                for j in i["items"]:
                    if j["isFolder"] == 1:
                        if await Api_menu.filter(
                            name=j["name"], api_service_id=service_id
                        ).exists():
                            menu = (
                                await Api_menu.filter(
                                    name=j["name"], api_service_id=service_id, type=1
                                )
                                .first()
                                .values()
                            )
                            menu_id = menu["id"]
                        else:
                            second_menu = await Api_menu.create(
                                name=j["name"],
                                type=1,
                                pid=first_id,
                                user_id=user_id,
                                status=1,
                                api_service_id=service_id,
                            )
                            menu_id = second_menu.id
                        for k in j["items"]:
                            try:
                                body_type, method = await handle_data(
                                    k["contentType"], k["httpMethod"]
                                )
                                params = await handle_params(k["queryParams"])
                                header = await handle_header(k["headerParams"])
                                body = await handle_body(k["requestParams"])
                                if (
                                    await Api.filter(
                                        api_service_id=service_id, url=k["url"]
                                    ).exists()
                                    or await Api.filter(
                                        api_service_id=service_id,
                                        url=service_name + k["url"],
                                    ).exists()
                                ):
                                    api_value = (
                                        await Api.filter(
                                            api_service_id=service_id, url=k["url"]
                                        )
                                        .first()
                                        .values()
                                    )
                                    req = {
                                        "body_type": body_type,
                                        "method": method,
                                        "header": header,
                                        "params": params,
                                        "params_id": None,
                                        "body": body,
                                        "before": api_value["req"]["before"],
                                        "after": api_value["req"]["after"],
                                        "form_data": api_value["req"]["form_data"],
                                        "form_urlencoded": api_value["req"][
                                            "form_urlencoded"
                                        ],
                                        "file_path": api_value["req"]["file_path"],
                                        "assert": api_value["req"]["assert"],
                                        "config": {
                                            "retry": 0,
                                            "req_timeout": 5,
                                            "res_timeout": 5,
                                        },
                                    }
                                    key_check = await handle_check(
                                        api_value["req"]["header"],
                                        api_value["req"]["params"],
                                        api_value["req"]["body"],
                                        header,
                                        params,
                                        body,
                                    )
                                    if k["url"] == "/game/upload/file":
                                        print("key_check=", json.dumps(key_check))
                                    if key_check:
                                        for m in key_check:
                                            if m["add"] or m["delete"]:
                                                await Api_update.create(
                                                    req=key_check,
                                                    api_id=api_value["id"],
                                                    user_id=user_id,
                                                    api_service_id=service_id,
                                                )
                                    if service_name not in api_value["url"]:
                                        k["url"] = service_name + k["url"]
                                    await Api.filter(
                                        api_service_id=service_id, url=api_value["url"]
                                    ).update(
                                        url=k["url"],
                                        req=req,
                                        user_id=user_id,
                                        document=k,
                                        update_time=datetime.now().strftime(
                                            "%Y-%m-%d %H:%M:%S"
                                        ),
                                    )
                                    update_num += 1
                                else:
                                    req = {
                                        "body_type": body_type,
                                        "method": method,
                                        "header": header,
                                        "params": params,
                                        "body": body,
                                        "before": [],
                                        "after": [],
                                        "form_data": [],
                                        "form_urlencoded": [],
                                        "file_path": [],
                                        "assert": [],
                                        "config": {
                                            "retry": 0,
                                            "req_timeout": 5,
                                            "res_timeout": 5,
                                        },
                                    }
                                    api_value = await Api.create(
                                        api_service_id=service_id,
                                        url=service_name + k["url"],
                                        req=req,
                                        user_id=user_id,
                                        document=k,
                                    )
                                    create_num += 1
                                    await Api_menu.create(
                                        name=k["name"] if k["name"] else k["url"],
                                        type=2,
                                        pid=menu_id,
                                        user_id=user_id,
                                        api_service_id=service_id,
                                        api_id=api_value.id,
                                        status=1,
                                    )
                            except Exception as e:
                                # print("handle_gitlab函数处理数据失败，原因：", k["url"])
                                pass

        return True
    except Exception as e:
        print("handle_gitlab函数执行失败，原因：", e)


async def handle_body(body):
    try:
        res_body = {}
        if body:
            for i in body:
                if i["type"] == "object":
                    if i["children"]:
                        res_body.update({i["name"]: await handle_object(i["children"])})
                elif i["type"] == "int32" or i["type"] == "int64":
                    res_body.update({i["name"]: i["example"]})
                elif i["type"] == "boolean":
                    res_body.update(
                        {
                            i["name"]: (
                                bool(i["example"])
                                if i["example"] != 0 or i["example"] == ""
                                else False
                            )
                        }
                    )
                elif i["type"] == "array":
                    res_body[i["name"]] = []
                    res = await handle_array(i["children"])
                    res_body[i["name"]].append(res)
                elif i["type"] == "string":
                    res_body.update({i["name"]: i["example"]})
                elif i["type"] == "float":
                    res_body.update({i["name"]: i["example"]})
                else:
                    res_body.update({i["name"]: str(i["example"])})
        return res_body
    except Exception as e:
        print("handle_body函数执行失败，原因：", e)


# 处理object数据类型的children
async def handle_object(children):
    try:
        res_children = {}
        for i in children:
            if i["type"] == "object":
                res_children.update({i["name"]: await handle_object(i["children"])})
            elif i["type"] == "int32" or i["type"] == "int64":
                res_children.update({i["name"]: i["example"]})
            elif i["type"] == "boolean":
                res_children.update({i["name"]: bool(i["example"])})
            elif i["type"] == "array":
                res_children[i["name"]] = []
                res = await handle_array(i["children"])
                res_children[i["name"]].append(res)
            elif i["type"] == "string":
                res_children.update({i["name"]: i["example"]})
            elif i["type"] == "float":
                res_children.update({i["name"]: i["example"]})
            else:
                res_children.update({i["name"]: str(i["example"])})
        return res_children
    except Exception as e:
        print("handle_object函数执行失败，原因：", e)


# 处理array数据类型的children
async def handle_array(children):
    try:
        res_children = {}
        for i in children:
            if i["type"] == "object":
                if i["children"]:
                    res_children.update({i["name"]: await handle_object(i["children"])})
            elif i["type"] == "int32" or i["type"] == "int64":
                res_children.update({i["name"]: i["example"]})
            elif i["type"] == "boolean":
                res_children.update({i["name"]: bool(i["example"])})
            elif i["type"] == "array":
                res_children[i["name"]] = []
                res = await handle_array(i["children"])
                res_children[i["name"]].append(res)
            elif i["type"] == "string":
                res_children.update({i["name"]: i["example"]})
            elif i["type"] == "float":
                res_children.update({i["name"]: i["example"]})
            else:
                res_children.update({i["name"]: str(i["example"])})
        return res_children
    except Exception as e:
        print("handle_children函数执行失败，原因：", e)


async def handle_header(header):
    try:
        res_headers = []
        if header:
            for i in header:
                res_headers.append(
                    {"key": i["name"], "value": i["example"], "status": True}
                )
        else:
            res_headers = [
                {"key": "Content-Type", "value": "application/json", "status": True}
            ]
        return res_headers
    except Exception as e:
        print("handle_header函数执行失败，原因：", e)


async def handle_params(params):
    try:
        res_params = []
        if params:
            for j in params:
                res_params.append(
                    {"key": j["name"], "value": j["example"], "status": True}
                )
        return res_params
    except Exception as e:
        print("handle_params函数执行失败，原因：", e)


async def handle_data(content_type, method):
    try:
        if "application/json" in content_type:
            body_type = 2
        elif "application/x-www-form-urlencoded" in content_type:
            body_type = 4
        elif "form-data" in content_type:
            body_type = 3
        else:
            body_type = 1

        if method == "GET" or method == "get":
            http_method = 1
        elif method == "POST" or method == "post":
            http_method = 2
        elif method == "PUT" or method == "put":
            http_method = 3
        elif method == "DELETE" or method == "delete":
            http_method = 4
        else:
            http_method = 2
        return body_type, http_method
    except Exception as e:
        print("handle_data函数执行失败，原因：", e)


async def handle_check(
    old_headers, old_params, old_body, new_headers, new_params, new_body
):
    try:
        if not new_body:
            new_body = {}
        header = await find_keys_not_in_params(old_headers, new_headers)
        params = await find_keys_not_in_params(old_params, new_params)
        body = await find_keys_not_in_a(old_body, new_body)

        delete_header = await find_keys_not_in_params(new_headers, old_headers)
        delete_params = await find_keys_not_in_params(new_params, old_params)
        delete_body = await find_keys_not_in_a(new_body, old_body)
        return [
            {"key": "headers", "add": header, "delete": delete_header},
            {"key": "params", "add": params, "delete": delete_params},
            {"key": "body", "add": body, "delete": delete_body},
        ]
    except Exception as e:
        print("handle_check函数执行失败，原因：", e)


async def find_keys_not_in_a(a, b, parent_key=""):
    try:
        keys_not_in_a = []
        for key in b:
            full_key = f"{parent_key}.{key}" if parent_key else key
            if key not in a:
                keys_not_in_a.append(full_key)
            elif isinstance(b[key], dict) and isinstance(a.get(key), dict):
                res = await find_keys_not_in_a(a[key], b[key], full_key)
                keys_not_in_a.extend(res)
            elif isinstance(b[key], list) and isinstance(a.get(key), list):
                for i, item in enumerate(b[key]):
                    if (
                        isinstance(item, dict)
                        and i < len(a[key])
                        and isinstance(a[key][i], dict)
                    ):
                        res = await find_keys_not_in_a(
                            a[key][i], item, f"{full_key}[{i}]"
                        )
                        keys_not_in_a.extend(res)
        return keys_not_in_a
    except Exception as e:
        print("find_keys_not_in_a函数执行失败，原因：", e)


async def find_keys_not_in_params(a_list, b_list):
    try:
        a_keys = {item["key"] for item in a_list}
        b_keys = {item["key"] for item in b_list}
        keys_not_in_a = b_keys - a_keys
        return list(keys_not_in_a)
    except Exception as e:
        print("find_keys_not_in_params函数执行失败，原因：", e)

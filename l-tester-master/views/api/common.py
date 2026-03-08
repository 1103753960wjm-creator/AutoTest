import json
import re
from views.api.api_model import Api_envs, Api_var

# body强转类型
async def json_body(body):
    try:
        body = json.loads(body)
        return body
    except Exception as e: 
        return str(e)

# 处理变量    
async def handle_var(env_id, data):
    try:
        if isinstance(data, str):
            if "{{" in data and "}}" in data:
                data = await find_var(env_id, data)
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    if "{{" in value and "}}" in value:
                        data[key] = await find_var(env_id, value)
                elif isinstance(value, dict):
                    data[key] = await handle_var(env_id, value)
                elif isinstance(value, list):
                    for item in value:
                        item = await handle_var(env_id, item)
        elif isinstance(data, list):
            for item in data:
                item = await handle_var(env_id, item)
        return data
    except Exception as e:
        return str(e)

# 查找变量-生成list
async def find_var(env_id, data):
    try:
        if "{{" in data and "}}" in data:
            key = re.findall(r"\{{(.+?)}}", data)
        for i in key:
            var = "{{" + i + "}}"
            res = await complete_var(env_id, var)
            data = data.replace(var, str(res))
        return data
    except Exception as e:
        return str(e)

async def complete_var(env_id, key):
    try:
        env_var = await Api_envs.filter(id=env_id).first().values()
        for i in env_var["config"]:
            if i["name"] == key:
                return i["value"]
        for j in env_var["variable"]:
            if j["name"] == key:
                return j["value"]
        all_var = await Api_var.filter(name=key).first().values()
        if all_var:
            return all_var["value"]
    except Exception as e:
        return str(e)
# 处理请求头
async def params_header(params):
    try:
        res = {}
        for i in params:
            if i["status"]:
                res.update({i["key"]: i["value"]})
        return res
    except Exception as e:
        return str(e)
# 请求域名
async def url_host(env_id, url):
    try:
        api_url = await handle_var(env_id, url)
        return api_url
    except Exception as e:
        return str(e)
    
async def compare_data(old_data, new_data, path=""):
    changes = []

    # 对字典处理
    if isinstance(old_data, dict) and isinstance(new_data, dict):
        all_keys = set(old_data.keys()).union(new_data.keys())
        for key in all_keys:
            old_val = old_data.get(key, "__key_missing__")
            new_val = new_data.get(key, "__key_missing__")
            sub_path = f"{path}.{key}" if path else key

            if old_val == "__key_missing__":
                changes.append({
                    "field": sub_path,
                    "type": "add",
                    "old": None,
                    "new": new_val
                })
            elif new_val == "__key_missing__":
                changes.append({
                    "field": sub_path,
                    "type": "delete",
                    "old": old_val,
                    "new": None
                })
            else:
                changes.extend(await compare_data(old_val, new_val, sub_path))

    # 对数组处理
    elif isinstance(old_data, list) and isinstance(new_data, list):
        max_len = max(len(old_data), len(new_data))
        for i in range(max_len):
            old_val = old_data[i] if i < len(old_data) else "__index_missing__"
            new_val = new_data[i] if i < len(new_data) else "__index_missing__"
            sub_path = f"{path}[{i}]"

            if old_val == "__index_missing__":
                changes.append({
                    "field": sub_path,
                    "type": "add",
                    "old": None,
                    "new": new_val
                })
            elif new_val == "__index_missing__":
                changes.append({
                    "field": sub_path,
                    "type": "delete",
                    "old": old_val,
                    "new": None
                })
            else:
                changes.extend(await compare_data(old_val, new_val, sub_path))

    else:
        if old_data != new_data:
            changes.append({
                "field": path,
                "type": "edit",
                "old": old_data,
                "new": new_data
            })

    return changes


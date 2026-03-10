import json
from urllib.parse import parse_qs

import yaml

from config.settings import mitmproxy_yaml_path


# 处理请求体
async def body_to_json(request):
    data = await request.body()
    body = {}
    if data:
        try:
            parsed = json.loads(data)
            if isinstance(parsed, dict):
                body = parsed
        except json.JSONDecodeError:
            body = {}

    headers = await header_to_json(request)
    authorization = headers.get("authorization", "")
    token = ""
    if authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    if not token:
        token = headers.get("x-token", "")
    user_id = headers.get("x-user-id", "")

    if token and not body.get("token"):
        body["token"] = token
    if user_id and not body.get("user_id"):
        body["user_id"] = user_id
    return body


# 处理请求头
async def header_to_json(request):
    header = dict([(k, v) for k, v in request.headers.items()])
    return header


# 处理接口路径参数
async def params_to_json(request):
    parts = str(request.query_params).split("&")
    params = {}
    for part in parts:
        key, value = part.split("=")
        params[key] = value
    return params


# 处理json转yaml
async def json_to_yaml(json_data):
    return yaml.safe_dump(json_data)


async def json_to_yaml_safe(json_data: str):
    """
    安全的JSON转YAML转换，处理各种边界情况

    Args:
        json_path: JSON数据
        yaml_path: YAML文件路径
        overwrite: 是否覆盖已存在的YAML文件
    """

    try:
        # 处理特殊值（如None, bool）
        def process_value(val):
            if val is None:
                return "null"
            elif isinstance(val, bool):
                return str(val).lower()
            elif isinstance(val, (dict, list)):
                return val
            else:
                return val

        # 递归处理所有值
        def process_dict(d):
            if isinstance(d, dict):
                return {k: process_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [process_dict(v) for v in d]
            else:
                return process_value(d)

        processed_data = process_dict(json_data)

        # 写入YAML
        with open(mitmproxy_yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(
                processed_data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                explicit_start=True,
                explicit_end=True,
                indent=2,
                width=80,
                line_break="\n",
            )
        return True, processed_data

    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        return False, []
    except yaml.YAMLError as e:
        print(f"❌ YAML写入错误: {e}")
        return False, []
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False, []

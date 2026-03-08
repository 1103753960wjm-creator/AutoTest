# 账号密码错误
import inspect
from views.warning_call.call_commom import send_notice


async def login_Exception():
    return {"code": 1000, "message": f"账号密码错误，请重新登录！", "data": {}}


# 捕捉异常返回
async def catch_Exception(e):
    # 获取完整的调用栈
    stack = inspect.stack()
    # stack[0] 是当前函数 (function_a)
    # stack[1] 是直接调用者
    caller_frame = stack[1]
    caller_name = caller_frame.function
    await send_notice(
        35,
        "error_notice",
        {"error_message": f"{caller_name}函数异常，原因：{str(e)}，速去查看"},
    )
    return {"code": 1001, "message": f"接口请求异常，原因是：{str(e)}", "data": {}}


# token鉴权失败
async def token_Exception(e):
    return {
        "code": 1002,
        "message": f"token鉴权失败，请重新登录后重试，失败原因是：{str(e)}",
        "data": {},
    }


# token已过期
async def token_expire():
    return {"code": 1003, "message": f"token已失效，请重新登录后重试！", "data": {}}


# 该账号已停用
async def user_false():
    return {"code": 1004, "message": f"该账号已停用，请联系管理员", "data": {}}


# 没有分配角色
async def role_Exception():
    return {"code": 1004, "message": f"该账号未分配角色，请联系-管理员", "data": {}}


# 没有操作权限
async def permission_Exception():
    return {"code": 1005, "message": f"没有操作权限，请联系-管理员", "data": {}}


# 登录成功
async def login_success(token, user_id, username, avatar):
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": token,
            "user_id": user_id,
            "username": username,
            "avatar": avatar,
        },
    }


# 退出登录成功
async def logout_success():
    return {"code": 200, "message": "退出登录成功", "data": {}}


# 请求成功
async def res_success(data):
    return {"code": 200, "message": "请求成功", "data": data}


# 启动app安装成功
async def install_success(data):
    return {"code": 200, "message": "启动app安装成功，等待安装中", "data": data}


# 启动app卸载成功
async def uninstall_success(data):
    return {"code": 200, "message": "启动app卸载成功，等待卸载中", "data": data}


# 启动成功
async def run_success(data):
    return {"code": 200, "message": "启动成功", "data": data}


# 正在执行
async def running(data):
    return {"code": 200, "message": "正在执行", "data": data}


# 执行结束
async def stop(data):
    return {"code": 200, "message": "执行结束", "data": data}


# 添加成功
async def add_success(data):
    return {"code": 200, "message": "添加成功", "data": data}


# 编辑成功
async def edit_success(data):
    return {"code": 200, "message": "编辑成功", "data": data}


# 保存成功
async def save_success(data):
    return {"code": 200, "message": "保存成功", "data": data}


# 删除成功
async def del_success(data):
    return {"code": 200, "message": "删除成功", "data": data}


async def del_fail(data):
    return {
        "code": 100,
        "message": "删除失败，该节点下有子节点，请先删除子节点",
        "data": data,
    }


# 上传图片成功
async def upload_img_success(data):
    return {"code": 200, "message": "上传图片成功", "data": data}


# 上传图片成功
async def upload_file_success(data):
    return {"code": 200, "message": "上传文件成功", "data": data}


# aab转apk成功
async def aab_to_apk_success(data):
    return {"code": 200, "message": "aab转apk成功", "data": data}


# aab转apk失败
async def aab_to_apk_fail(msg):
    return {
        "code": 100,
        "message": msg,
    }


async def res_fail(msg):
    return {"code": 10001, "message": msg}


async def res_error(msg, data):
    return {"code": 10002, "message": msg, "data": data}

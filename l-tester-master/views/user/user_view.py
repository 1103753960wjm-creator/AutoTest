from datetime import datetime, timedelta, timezone
import json
from fastapi import Request
from fastapi import APIRouter

from common.db_curd import db_delete
from common.encryption import encrypt_md5
from common.paginate import db_page_all
from common.request_to_json import body_to_json
from common.return_code import (
    catch_Exception,
    login_Exception,
    login_success,
    logout_success,
    res_success,
    add_success,
    edit_success,
    del_success,
)
from common.table_tree import create_tree
from common.time_str import time_to_str
from middleware.token_auth import create_token
from views.user.user_model import (
    Permission,
    Role,
    Role_permission,
    Role_user,
    User_info,
    User_info_log,
    User_info_login_log,
)

router = APIRouter(prefix="/api/user")


@router.post("/login")
async def login(request: Request):
    try:
        body = await body_to_json(request)
        user = await User_info.get(account=body["username"], password=body["password"])
        if user:
            if user.token_time < datetime.now(timezone(timedelta(hours=8))):
                token = await create_token(request)
                await User_info.filter(id=user.id).update(
                    token=token, token_time=datetime.now() + timedelta(days=7)
                )
                return await login_success(token, user.id, user.username, user.avatar)
            else:
                return await login_success(
                    user.token, user.id, user.username, user.avatar
                )
        else:
            return await login_Exception()
    except Exception as e:
        return await login_Exception()


@router.post("/logout")
async def logout(request: Request):
    body = await body_to_json(request)
    await User_info.filter(id=body["user_id"]).update(token="")
    return await logout_success()


@router.post("/user_list")
async def user_list(request: Request):
    try:
        data = await db_page_all(
            User_info,
            request,
            key=["token", "token_time", "password", "account"],
            order="-id",
        )
        for i in data["content"]:
            role = await Role_user.filter(user_id=i["id"]).first().values()
            if role:
                role_data = await Role.filter(id=role["role_id"]).first().values()
                i["role_name"] = role_data["name"]
            else:
                i["role_name"] = "未分配角色"
        return await res_success(data)
    except Exception as e:
        print(e)
        return await catch_Exception(e)


@router.post("/user_select")
async def user_select(request: Request):
    try:
        result = []
        body = await body_to_json(request)
        user = await User_info.all().values()
        for i in user:
            result.append(
                {
                    "name": i["username"],
                    "email": i["email"],
                    "id": i["id"],
                    "account": i["account"],
                }
            )
        return await res_success(result)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/add_user")
async def add_user(request: Request):
    try:
        body = await body_to_json(request)
        await User_info.create(
            account=body["account"],
            username=body["username"],
            password=body["password"],
            avatar=body["avatar"],
            phone=body["phone"],
            email=body["email"],
            status=body["status"],
            token="xxx",
            token_time=datetime.now(),
        )
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/edit_user")
async def add_user(request: Request):
    try:
        body = await body_to_json(request)
        await User_info.filter(id=body["id"]).update(
            avatar=body["avatar"],
            phone=body["phone"],
            email=body["email"],
            status=body["status"],
        )
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/edit_password")
async def edit_password(request: Request):
    try:
        body = await body_to_json(request)
        confirm_password = await encrypt_md5(body["confirm_password"])
        password = await encrypt_md5(body["password"])
        if (
            await Role_user.filter(user_id=body["user_id"], role_id=1)
            and body["confirm_password"] != ""
            and body["password"] != ""
        ):
            await User_info.filter(id=body["id"]).update(password=confirm_password)
            return await edit_success({})
        user = await User_info.filter(id=body["id"]).first().values()
        if body["user_id"] != user["id"]:
            return await catch_Exception("只能修改自己的密码！！！")
        if (
            user
            and password == user["password"]
            and body["confirm_password"] != ""
            and body["password"] != ""
        ):
            await User_info.filter(id=body["user_id"]).update(password=confirm_password)
            return await edit_success({})
        else:
            return await catch_Exception("用户不存在或旧密码不匹配，请重试！！！")
    except Exception as e:
        return await catch_Exception(e)


@router.post("/del_user")
async def add_user(request: Request):
    try:
        await db_delete(User_info, request)
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/login_log")
async def login_log(request: Request):
    try:
        data = await db_page_all(User_info_login_log, request, [], order="-id")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/action_log")
async def action_log(request: Request):
    try:
        data = await db_page_all(User_info_log, request, [], order="-id")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/role_list")
async def role_list(request: Request):
    try:
        data = await db_page_all(Role, request, [], order="-id")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/role_select")
async def role_select(request: Request):
    try:
        result = []
        res = await Role.all()
        for i in res:
            result.append({"value": i.id, "name": i.name})
        return await res_success(result)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/add_role")
async def add_role(request: Request):
    try:
        body = await body_to_json(request)
        await Role.create(name=body["name"], user_id=body["user_id"])
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/edit_role")
async def edit_role(request: Request):
    try:
        body = await body_to_json(request)
        await Role.filter(id=body["id"]).update(
            name=body["name"],
            user_id=body["user_id"],
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/del_role")
async def del_role(request: Request):
    try:
        await db_delete(Role, request)
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/permission_tree")
async def permission_tree(request: Request):
    try:
        data = await create_tree(
            model=Permission, fields=["id", "name", "pid", "type", "url"], search={}
        )
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/role_permission")
async def role_permission(request: Request):
    try:
        body = await body_to_json(request)
        res = []
        if body["role_id"] == 1:
            data = await Permission.all()
            for i in data:
                res.append(i.id)
        else:
            data = await Role_permission.filter(role_id=body["role_id"])
            for i in data:
                res.append(i.permission_id)
        return await res_success(res)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/add_permission")
async def add_permission(request: Request):
    try:
        body = await body_to_json(request)
        await Permission.create(
            name=body["name"],
            pid=body["pid"],
            type=body["type"],
            url=body["url"] if body["url"] != "" else "",
            user_id=body["user_id"],
        )
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/edit_permission")
async def edit_permission(request: Request):
    try:
        body = await body_to_json(request)
        await Permission.filter(id=body["id"]).update(
            name=body["name"], url=body["url"], user_id=body["user_id"]
        )
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/del_permission")
async def del_permission(request: Request):
    try:
        await db_delete(Permission, request)
        body = await body_to_json(request)
        await Role_permission.filter(permission_id=body["id"]).delete()
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/edit_role_permission")
async def add_role_permission(request: Request):
    try:
        body = await body_to_json(request)
        await Role_permission.filter(role_id=body["role_id"]).delete()
        for i in body["permission"]:
            await Role_permission.create(role_id=body["role_id"], permission_id=i)
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/change_role_user")
async def change_role_user(request: Request):
    try:
        body = await body_to_json(request)
        for i in body["user_list"]:
            role = Role_user.filter(user_id=i)
            if await role.count() > 0:
                await role.update(role_id=body["role_id"])
            else:
                await Role_user.create(role_id=body["role_id"], user_id=i)
        return await res_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/role_user")
async def role_user(request: Request):
    try:
        body = await body_to_json(request)
        data = await Role_user.filter(role_id=body["role_id"]).values()
        res = await time_to_str(data)
        return await res_success(res)
    except Exception as e:
        return await catch_Exception(e)

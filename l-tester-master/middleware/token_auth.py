from datetime import datetime, timedelta, timezone
from fastapi import Request
from fastapi_pagination import response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from urllib3.util import url
from common.encryption import encrypt_md5
from common.request_to_json import body_to_json
from common.return_code import (
    permission_Exception,
    role_Exception,
    token_Exception,
    token_expire,
    user_false,
)
from config.auth_white import white_list
from views.user.user_model import Permission, Role_permission, Role_user, User_info


async def create_token(request):
    body = await body_to_json(request)
    key = datetime.now()
    token = await encrypt_md5(str(body["username"]) + str(body["password"]) + str(key))
    return token


class Token_Auth(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            url_path = request.url.path
            if (
                url_path in white_list
                or "/media/" in url_path
                or url_path == "/api/user/login"
                or url_path == "/api/user/logout"
            ):
                response = await call_next(request)
                return response

            body = await body_to_json(request)
            token = body["token"]
            user = await User_info.get(id=body["user_id"])
            if user.status == "0":
                response = await user_false()
                return JSONResponse(response)
            role = await Role_user.filter(user_id=body["user_id"]).first().values()
            if role["role_id"] == 1 and body["token"] == user.token:
                response = await call_next(request)
                return response
            if role is None:
                response = await role_Exception()
                return JSONResponse(response)
            permission = await Permission.filter(url=url_path).first().values()
            if permission:
                role_permission = (
                    await Role_permission.filter(
                        role_id=role["role_id"], permission_id=permission["id"]
                    )
                    .first()
                    .values()
                )
                if role_permission:
                    return await call_next(request)
                else:
                    response = await permission_Exception()
                    return JSONResponse(response)

            if token != user.token or user.token_time < datetime.now(
                timezone(timedelta(hours=8))
            ):
                response = await token_expire()
                return JSONResponse(response)
            else:
                response = await call_next(request)
                return response
        except Exception as e:
            response = await token_Exception(e)
            return JSONResponse(response)

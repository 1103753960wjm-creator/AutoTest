"""日志中间件."""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from fastapi import Response
from loguru import logger
from config.auth_white import white_list
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from views.user.user_model import User_info_log, User_info_login_log


class Logger_Middleware(BaseHTTPMiddleware):
    """日志类."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """重写dispatch方法.

        Args:
            request (Request): Request.
            call_next (_type_): 回调函数.

        Returns:
            Response: Response.
        """
        try:
            self.logger = logger
            method = request.method
            scop = {
                key.decode("utf-8"): value.decode("utf-8")
                for key, value in request.scope["headers"]
            }
            if "x-forwarded-for" in scop.keys():
                ip = scop["x-forwarded-for"]
            else:
                ip = request.client.host
            body = await request.body()
            path = request.scope["path"]
            if path in white_list:
                return await call_next(request)
            china_tz = timezone(timedelta(hours=8), "China")
            current_time_china = datetime.now(china_tz)
            formatted_time = current_time_china.strftime("%Y-%m-%d")
            response = await call_next(request)
            self.logger.remove()
            code = response.status_code
            INFO = f"{ip}__{code}__{method}__{path}"
            if code != 200:
                log_path = os.path.join("./log/error", f"{formatted_time}_error.log")
                self.logger.add(
                    log_path, encoding="utf-8", rotation="7 days", enqueue=True
                )
                self.logger.error(INFO)
            else:
                log_path = os.path.join("./log/info", f"{formatted_time}_info.log")
                self.logger.add(
                    log_path, encoding="utf-8", rotation="7 days", enqueue=True
                )
                self.logger.info(INFO)
            if method != "GET" and path not in [
                "/api/common/upload_image",
                "/api/common/upload_file",
                "/api/common/upload_airtest_img",
            ]:
                response_body = b"".join(
                    [chunk async for chunk in response.body_iterator]
                )
                response.body_iterator = iter([response_body])
                response_data = json.loads(response_body.decode("utf-8"))
            else:
                return response

            if path in [
                "/api/user/login_log",
                "/api/user/action_log",
                "/api/api/service_api_update",
            ]:
                new_response = Response(
                    content=response_body,
                    status_code=int(response.status_code),
                    headers=dict(response.headers),
                )
                return new_response
            elif path == "/api/user/login":
                user = json.loads(body)["username"]
                await User_info_login_log.create(
                    login_user=user,
                    login_ip=ip,
                    login_result=response_data["message"],
                )
            else:
                user = json.loads(body)["user_id"]

                await User_info_log.create(
                    user_id=user,
                    log_api=path,
                    log_content=body,
                    log_status=(
                        response_data["code"]
                        if "code" in response_data
                        else response.status_code
                    ),
                    log_result=response_data,
                    log_ip=ip,
                )
            new_response = Response(
                content=response_body,
                status_code=int(response.status_code),
                headers=dict(response.headers),
            )
            return new_response
        except Exception as e:
            # Re-raise so Starlette's error handlers can craft a valid response.
            self.logger.error(f"异常：{str(e)}")
            raise

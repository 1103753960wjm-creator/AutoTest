import json

from fastapi import APIRouter, Request

from common.return_code import catch_Exception, res_fail, res_success, save_success
from views.ai.ai_service import AIGatewayService


router = APIRouter(prefix="/api/ai")


async def _request_json_or_empty(request: Request):
    body = await request.body()
    if not body:
        return {}
    return json.loads(body)


@router.post("/mode_info")
async def mode_info(request: Request):
    try:
        body = await _request_json_or_empty(request)
        data = AIGatewayService().get_mode_info(body.get("mode"))
        return await res_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)


@router.post("/config_info")
async def config_info(request: Request):
    try:
        await _request_json_or_empty(request)
        data = AIGatewayService().get_config_info()
        return await res_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)


@router.post("/save_config")
async def save_config(request: Request):
    try:
        body = await _request_json_or_empty(request)
        data = AIGatewayService().save_config(body)
        return await save_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)


@router.post("/generate_testcases")
async def generate_testcases(request: Request):
    try:
        body = await _request_json_or_empty(request)
        data = AIGatewayService().generate_test_cases(body)
        return await res_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)

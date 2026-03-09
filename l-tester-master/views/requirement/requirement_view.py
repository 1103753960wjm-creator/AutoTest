from fastapi import APIRouter, Request

from common.request_to_json import body_to_json
from common.return_code import catch_Exception, res_fail, res_success, save_success
from views.requirement.requirement_common import (
    list_page_requirements,
    list_recent_requirements,
    save_reviewed_cases,
)


router = APIRouter(prefix="/api/requirement")


@router.post("/save_reviewed_cases")
async def save_reviewed_cases_api(request: Request):
    try:
        body = await body_to_json(request)
        data = await save_reviewed_cases(body)
        return await save_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)


@router.post("/list_recent")
async def list_recent_api(request: Request):
    try:
        body = await body_to_json(request)
        data = await list_recent_requirements(
            int(body.get("user_id") or 0), body.get("limit") or 10
        )
        return await res_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)


@router.post("/list_page")
async def list_page_api(request: Request):
    try:
        body = await body_to_json(request)
        data = await list_page_requirements(body)
        return await res_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)

from fastapi import APIRouter, Request

from common.request_to_json import body_to_json
from common.return_code import catch_Exception, res_fail, res_success, save_success
from views.automation_draft.automation_draft_common import (
    generate_automation_draft,
    get_automation_draft_info,
    list_testcase_automation_drafts,
    save_automation_draft,
)


router = APIRouter(prefix="/api/automation_draft")


@router.post("/generate")
async def generate(request: Request):
    try:
        body = await body_to_json(request)
        data = await generate_automation_draft(body)
        return await res_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)


@router.post("/get_info")
async def get_info(request: Request):
    try:
        body = await body_to_json(request)
        data = await get_automation_draft_info(body)
        return await res_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)


@router.post("/list_by_testcase")
async def list_by_testcase(request: Request):
    try:
        body = await body_to_json(request)
        data = await list_testcase_automation_drafts(body)
        return await res_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)


@router.post("/save_to_asset")
async def save_to_asset(request: Request):
    try:
        body = await body_to_json(request)
        data = await save_automation_draft(body)
        return await save_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)

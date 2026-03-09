from fastapi import APIRouter, Request

from common.request_to_json import body_to_json
from common.return_code import catch_Exception, edit_success, res_fail, res_success
from views.requirement.requirement_common import list_requirement_testcases
from views.testcase.testcase_common import (
    list_page_testcases,
    update_testcase_review_status,
)


router = APIRouter(prefix="/api/testcase")


@router.post("/list_by_requirement")
async def list_by_requirement(request: Request):
    try:
        body = await body_to_json(request)
        data = await list_requirement_testcases(
            int(body.get("requirement_id") or 0), int(body.get("user_id") or 0)
        )
        return await res_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)


@router.post("/list_page")
async def list_page(request: Request):
    try:
        body = await body_to_json(request)
        data = await list_page_testcases(body)
        return await res_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)


@router.post("/update_review_status")
async def update_review_status(request: Request):
    try:
        body = await body_to_json(request)
        data = await update_testcase_review_status(body)
        return await edit_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)

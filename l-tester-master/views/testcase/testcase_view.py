from urllib.parse import quote

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from common.request_to_json import body_to_json
from common.return_code import catch_Exception, edit_success, res_fail, res_success
from views.requirement.requirement_common import list_requirement_testcases
from views.testcase.testcase_common import (
    batch_update_testcases,
    compare_testcase_revisions,
    edit_testcase_content,
    export_testcases_excel,
    get_testcase_history,
    list_testcase_tags,
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


@router.post("/update_content")
async def update_content(request: Request):
    try:
        body = await body_to_json(request)
        data = await edit_testcase_content(body)
        return await edit_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)


@router.post("/batch_update")
async def batch_update(request: Request):
    try:
        body = await body_to_json(request)
        data = await batch_update_testcases(body)
        return await edit_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)


@router.post("/list_history")
async def list_history(request: Request):
    try:
        body = await body_to_json(request)
        data = await get_testcase_history(body)
        return await res_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)


@router.post("/compare_revisions")
async def compare_revisions(request: Request):
    try:
        body = await body_to_json(request)
        data = await compare_testcase_revisions(body)
        return await res_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)


@router.post("/list_tags")
async def list_tags(request: Request):
    try:
        body = await body_to_json(request)
        data = await list_testcase_tags(body)
        return await res_success(data)
    except ValueError as exc:
        return await res_fail(str(exc))
    except Exception as exc:
        return await catch_Exception(exc)


@router.post("/export_excel")
async def export_excel(request: Request):
    try:
        body = await body_to_json(request)
        filename, content = await export_testcases_excel(body)
        return Response(
            content=content,
            media_type="application/vnd.ms-excel; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"
            },
        )
    except ValueError as exc:
        result = await res_fail(str(exc))
        return JSONResponse(result, status_code=400)
    except Exception as exc:
        result = await catch_Exception(exc)
        return JSONResponse(result, status_code=500)

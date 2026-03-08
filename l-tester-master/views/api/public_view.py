from fastapi import APIRouter, Request
from common.db_curd import db_delete
from common.paginate import db_page_all
from common.request_to_json import body_to_json
from common.return_code import add_success, catch_Exception, del_success, edit_success, res_success
from views.api.api_model import Api_code, Api_function, Api_params

router = APIRouter(prefix="/api/api")

@router.post("/api_code")
async def api_code(request: Request):
    try:
        data = await db_page_all(Api_code, request, [], "id")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/add_code")
async def add_code(request: Request):
    try:
        body = await body_to_json(request)
        await Api_code.create(
            name=body["name"],
            code=body["code"],
            user_id=body["user_id"]
        )
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/del_code")
async def del_code(request: Request):
    try:
        await db_delete(Api_code, request)
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)
@router.post("/edit_code")
async def edit_code(request: Request):
    try:
        body = await body_to_json(request)
        await Api_code.filter(id=body["id"]).update(name=body["name"], code=body["code"], user_id=body["user_id"])
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/api_function")
async def api_function(request: Request):
    try:
        data = await db_page_all(Api_function, request, [], "-id")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/add_function")
async def add_function(request: Request):
    try:
        body = await body_to_json(request)
        await Api_function.create(
            name=body["name"],
            description=body["description"],
            user_id=body["user_id"]
        )
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/del_function")
async def del_function(request: Request):
    try:
        await db_delete(Api_function, request)
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/edit_function")
async def edit_function(request: Request):
    try:
        body = await body_to_json(request)
        await Api_function.filter(id=body["id"]).update(name=body["name"], description=body["description"], user_id=body["user_id"])
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/api_params")
async def api_params(request: Request):
    try:
        data = await db_page_all(Api_params, request, [], "-id")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/add_params")
async def add_params(request: Request):
    try:
        body = await body_to_json(request)
        await Api_params.create(
            name=body["name"],
            value=body["value"],
            user_id=body["user_id"]
        )
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/del_params")
async def del_params(request: Request):
    try:
        await db_delete(Api_params, request)
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/edit_params")
async def edit_params(request: Request):
    try:
        body = await body_to_json(request)
        await Api_params.filter(id=body["id"]).update(name=body["name"], value=body["value"], user_id=body["user_id"])
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/params_select")
async def params_select(request: Request):
    try:
        body = await body_to_json(request)
        data = await Api_params.all().values("id", "name", "value")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)
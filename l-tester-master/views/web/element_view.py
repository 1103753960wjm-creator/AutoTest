from datetime import datetime
from fastapi import APIRouter, Request
from common.db_curd import db_delete
from common.paginate import db_page_all
from common.request_to_json import body_to_json
from common.return_code import add_success, catch_Exception, del_success, edit_success, res_success
from common.table_tree import create_tree, del_tree_node
from views.web.web_model import Web_element, Web_element_menu

router = APIRouter(prefix="/api/web_element")

@router.post("/element_tree")
async def element_tree(request: Request):
    try:
        data = await create_tree(model=Web_element_menu, fields=["id", "name", "pid", "type"], search={})
        res = await del_tree_node(data, 2)
        return await res_success(res)
    except Exception as e:
        return await catch_Exception(e)

@router.post("/add_menu")
async def add_menu(request: Request):
    try:
        body = await body_to_json(request)
        await Web_element_menu.create(
            name=body["name"],
            pid=body["pid"],
            type=body["type"],
            user_id=body["user_id"],
        )
        return await add_success({})
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/edit_menu")
async def edit_menu(request: Request):
    try:
        body = await body_to_json(request)
        await Web_element_menu.filter(id=body["id"]).update(name=body["name"])
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/del_menu")
async def del_menu(request: Request):
    try:
        await db_delete(Web_element_menu, request)
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)

@router.post("/get_element_list")
async def get_element_list(request: Request):
    try:
        data = await db_page_all(Web_element, request, key=["user_id"], order="-id")
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/add_element")
async def add_element(request: Request):
    try:
       body = await body_to_json(request)
       element = await Web_element.create(
            name=body["name"],
            element=body["element"],
            user_id=body["user_id"],
            menu_id=body["menu_id"]
        )
       await Web_element_menu.create(
            name=body["name"],
            pid=body["menu_id"],
            type=2,
            user_id=body["user_id"],
            element_id=element.id
       )
       return await add_success({})
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/edit_element")
async def edit_element(request: Request):
    try:
        body = await body_to_json(request)
        await Web_element.filter(id=body["id"]).update(
            name=body["name"],
            element=body["element"],
            user_id=body["user_id"],
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        await Web_element_menu.filter(element_id=body["id"]).update(name=body["name"])
        return await edit_success({})
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/del_element")
async def del_element(request: Request):
    try:
        body = await body_to_json(request)
        await db_delete(Web_element, request)
        await Web_element_menu.filter(element_id=body["id"]).delete()
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)
    
@router.post("/get_element_select")
async def get_element_select(request: Request):
    try:
        data = await create_tree(model=Web_element_menu, fields=["id", "name", "pid", "type", "element_id"], search={})
        return await res_success(data)
    except Exception as e:
        return await catch_Exception(e)


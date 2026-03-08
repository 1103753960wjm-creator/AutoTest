# 作者：小林
from datetime import datetime

from fastapi import APIRouter
from fastapi import Request

from common.db_curd import db_delete
from common.paginate import db_page_all
from common.request_to_json import body_to_json
from common.return_code import catch_Exception, del_success, res_success
from common.time_str import time_to_str, img_review
from views.app.app_model import App_menu
from views.common.upload_model import airtest_img

router = APIRouter(prefix="/api/app")


@router.post("/img_list")
async def img_list(request: Request):
    try:
        data = await db_page_all(airtest_img, request, [], "-id")
        res = await img_review(data["content"])
        data["content"] = res
        result = await time_to_str(data)
        return await res_success(result)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/img_select")
async def img_select(request: Request):
    try:
        menu = await App_menu.filter(type=1).values()
        result = []
        for i in menu:
            menu_dict = {
                "value": i["id"],
                "label": i["name"],
                "children": [],
                "file_path": "",
            }
            imgs = await airtest_img.filter(menu=i["id"])
            if imgs:
                for j in imgs:
                    menu_dict["children"].append(
                        {"value": j.id, "label": j.file_name, "file_path": j.file_path}
                    )
                menu_dict["children"] = await img_review(menu_dict["children"])
            result.append(menu_dict)
        return await res_success(result)
    except Exception as e:
        return await catch_Exception(e)


@router.post("/delete_img")
async def delete_img(request: Request):
    try:
        await db_delete(airtest_img, request)
        return await del_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/edit_img")
async def edit_img(request: Request):
    try:
        data = await body_to_json(request)
        await airtest_img.filter(id=data["id"]).update(
            file_name=data["file_name"], file_path=data["file_path"]
        )
        return await res_success({})
    except Exception as e:
        return await catch_Exception(e)

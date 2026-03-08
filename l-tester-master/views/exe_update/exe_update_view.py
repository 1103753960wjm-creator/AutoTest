from fastapi import APIRouter, Request
from common.request_to_json import body_to_json
from common.return_code import catch_Exception, res_success
from views.exe_update.exe_update_model import exe_update_version


router = APIRouter(prefix="/api/exe_update")


@router.post("/update_version")
async def update_version(request: Request):
    try:
        body = await body_to_json(request)
        # await exe_update_version.create(
        #     name=body["version"], size=body["size"], version=body["version"]
        # )
        return await res_success({})
    except Exception as e:
        return await catch_Exception(e)


@router.post("/check_update")
async def check_update(request: Request):
    try:
        body = await body_to_json(request)
        print(body)
        version = body["old_version"]
        update_version = await exe_update_version.all().first().values()
        if update_version["version"] > version:
            return await res_success(
                {
                    "update": True,
                    "url": update_version["url"],
                    "version": update_version["version"],
                }
            )
        else:
            return await res_success({"update": False, "version": ""})
    except Exception as e:
        return await catch_Exception(e)

from tortoise import Tortoise
from common.request_to_json import body_to_json
from common.time_str import time_to_str
from db_settings import (
    Mysql_Database,
    Mysql_Host,
    Mysql_Port,
    Mysql_password,
    Mysql_username,
)
from views.user.user_model import User_info


# 下拉列表专用
async def db_select_all(db):
    data = await db.all()
    result = []
    for i in data:
        res = {"id": i.id, "name": i.name}
        result.append(res)
    return {"content": result}


# 根据id查询数据
async def db_select_id(db, id):
    data = await db.filter(id=id).first().values()
    result = await time_to_str(data)
    return result


# 删除数据
async def db_delete(db, request):
    try:
        body = await body_to_json(request)
        await db.filter(id=body["id"]).delete()
        return True, "删除成功"
    except Exception as e:
        return False, str(e)


# 初始化数据库连接
async def init_db():
    await Tortoise.init(
        db_url=f"mysql://{Mysql_username}:{Mysql_password}@{Mysql_Host}:{Mysql_Port}/{Mysql_Database}",
        modules={
            "models": [
                "aerich.models",
                "views.user.user_model",
                "views.common.upload_model",
                "views.app.app_model",
                "views.sdk.sdk_model",
                "views.web.web_model",
            ]
        },
    )
    # await Tortoise.generate_schemas()

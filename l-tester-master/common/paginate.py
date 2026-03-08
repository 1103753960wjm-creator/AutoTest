import json
from re import search

from common.request_to_json import body_to_json
from common.time_str import img_review, time_to_str
from views.user.user_model import User_info


# 分页查询
async def db_page_all(db, request, key, order):
    body = await body_to_json(request)  # body就是前端的传参
    search_dict = {k: v for k, v in body["search"].items() if v != ""}  # 查询条件
    db_select = db.filter(**search_dict)
    data = (
        await db_select.offset((body["currentPage"] - 1) * body["pageSize"])
        .limit(body["pageSize"])
        .order_by(order)
        .values()
    )
    result = await time_to_str(data)
    res = await remove_key(result, key)
    count = await db_select.count()
    return {
        "content": res,
        "currentPage": body["currentPage"],
        "pageSize": body["pageSize"],
        "total": count,
    }


async def remove_key(data, key):
    result = []
    for i in data:
        var = {k: v for k, v in i.items() if k not in key}
        result.append(var)
    return result

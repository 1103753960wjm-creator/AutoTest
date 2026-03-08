from datetime import datetime
import pytz
from config.settings import source_ip
from views.user.user_model import User_info


# 处理时区的时间格式
async def time_to_str(data):
    if isinstance(data, dict):
        if "user_id" in data.keys():
            user = await User_info.get(id=data["user_id"])
            data["username"] = user.username

        if "create_time" in data.keys() and data["create_time"] is not None:
            data["create_time"] = await time_utc(data["create_time"])

        if "update_time" in data.keys() and data["update_time"] is not None:
            data["update_time"] = await time_utc(data["update_time"])

        if "end_time" in data.keys() and data["end_time"] is not None:
            data["end_time"] = await time_utc(data["end_time"])

        if "start_time" in data.keys() and data["start_time"] is not None:
            data["start_time"] = await time_utc(data["start_time"])

        if "token_time" in data.keys() and data["token_time"] is not None:
            data["token_time"] = await time_utc(data["token_time"])

    elif isinstance(data, list):
        for i in data:
            if "user_id" in i.keys():
                user = await User_info.get(id=i["user_id"])
                i["username"] = user.username

            if "create_time" in i.keys() and i["create_time"] is not None:
                i["create_time"] = await time_utc(i["create_time"])

            if "update_time" in i.keys() and i["update_time"] is not None:
                i["update_time"] = await time_utc(i["update_time"])

            if "token_time" in i.keys() and i["token_time"] is not None:
                i["token_time"] = await time_utc(i["token_time"])

            if "end_time" in i.keys() and i["end_time"] is not None:
                i["end_time"] = await time_utc(i["end_time"])

            if "start_time" in i.keys() and i["start_time"] is not None:
                i["start_time"] = await time_utc(i["start_time"])
    return data


# 将服务器时间转成东八区
async def time_utc(utc_time_str):
    # 解析为 UTC datetime 对象
    utc_time = datetime.strftime(utc_time_str, "%Y-%m-%d %H:%M:%S")

    return utc_time


async def img_review(data):
    if isinstance(data, dict):
        if "file_path" in data.keys():
            data["file_path"] = source_ip + data["file_path"]
        if "before_img" in data.keys() and data["before_img"] != "":
            data["before_img"] = source_ip + data["before_img"]
        if "after_img" in data.keys() and data["after_img"] != "":
            data["after_img"] = source_ip + data["after_img"]
        if "video" in data.keys() and data["video"] != "":
            data["video"] = source_ip + data["video"]
        if "img" in data.keys() and data["img"] != "":
            data["img"] = source_ip + data["img"]
        if "trace" in data.keys() and data["trace"] != "":
            data["trace"] = source_ip + data["trace"]
    elif isinstance(data, list):
        for i in data:
            if "file_path" in i.keys():
                i["file_path"] = source_ip + i["file_path"]
            if "before_img" in i.keys() and i["before_img"] != "":
                i["before_img"] = source_ip + i["before_img"]
            if "after_img" in i.keys() and i["after_img"] != "":
                i["after_img"] = source_ip + i["after_img"]
            if "video" in i.keys() and i["video"] != "":
                i["video"] = source_ip + i["video"]
            if "img" in i.keys() and i["img"] != "":
                i["img"] = source_ip + i["img"]
            if "trace" in i.keys() and i["trace"] != "":
                i["trace"] = source_ip + i["trace"]
    return data

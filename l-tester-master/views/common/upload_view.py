# 作者：小林
from typing import List
from fastapi import APIRouter
from fastapi import File, UploadFile
from pathlib import Path
from datetime import datetime
from common.return_code import upload_img_success, catch_Exception, upload_file_success
from views.common.upload_model import airtest_img, upload_img

router = APIRouter(prefix="/api/common")

# 设置图片上传目录
BASE_IMG_DIR = Path("media/img")
BASE_IMG_DIR.mkdir(parents=True, exist_ok=True)

# 设置文件上传目录
BASE_FILE_DIR = Path("media/file")
BASE_FILE_DIR.mkdir(parents=True, exist_ok=True)

# 设置APP图片上传目录
BASE_APP_DIR = Path("media/app_img")
BASE_APP_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    try:
        # 获取当前日期，用于创建按年/月/日存储图片的目录
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        day = current_date.day

        # 根据年/月/日创建目录路径
        folder_path = BASE_IMG_DIR / str(year) / str(month).zfill(2) / str(day).zfill(2)
        folder_path.mkdir(parents=True, exist_ok=True)

        # 获取文件名
        file_name = file.filename
        file_path = folder_path / file_name

        # 将上传的文件保存到指定路径
        with open(file_path, "wb") as f:
            content = await file.read()  # 读取文件内容
            f.write(content)

        # 返回图片的 URL 或成功响应
        file_url = f"/media/img/{year}/{month:02d}/{day:02d}/{file_name}"
        res = {"file_url": file_url}
        return await upload_img_success(res)

    except Exception as e:
        return await catch_Exception(e)


@router.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 获取当前日期，用于创建按年/月/日存储图片的目录
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        day = current_date.day

        # 根据年/月/日创建目录路径
        folder_path = (
            BASE_FILE_DIR / str(year) / str(month).zfill(2) / str(day).zfill(2)
        )
        folder_path.mkdir(parents=True, exist_ok=True)

        # 获取文件名
        file_name = file.filename
        file_path = folder_path / file_name

        # 将上传的文件保存到指定路径
        with open(file_path, "wb") as f:
            content = await file.read()  # 读取文件内容
            f.write(content)

        # 返回图片的 URL 或成功响应
        file_url = f"/media/file/{year}/{month:02d}/{day:02d}"
        res = {"file_url": file_url, "filename": file_name}
        await upload_img.create(file_name=file_name, file_path=file_url)
        return await upload_file_success(res)

    except Exception as e:
        return await catch_Exception(e)


@router.post("/upload_airtest_img")
async def upload_airtest_img(file: UploadFile = File(...), menu_id: int = 0):
    try:

        # 根据年/月/日创建目录路径
        folder_path = BASE_APP_DIR
        folder_path.mkdir(parents=True, exist_ok=True)

        # 获取文件名
        file_name = file.filename
        file_path = folder_path / file_name

        # 将上传的文件保存到指定路径
        with open(file_path, "wb") as f:
            content = await file.read()  # 读取文件内容
            f.write(content)

        # 返回图片的 URL 或成功响应
        file_url = f"/media/app_img/{file_name}"
        res = {"file_url": file_url, "filename": file_name}
        await airtest_img.create(
            file_name=file_name, file_path=file_url, menu_id=menu_id
        )
        return await upload_img_success(res)

    except Exception as e:
        return await catch_Exception(e)

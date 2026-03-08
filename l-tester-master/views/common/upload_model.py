# 作者：小林
from tortoise import fields, Model


class upload_img(Model):
    file_name = fields.CharField(max_length=255, description="图片名称")
    file_path = fields.TextField(description="图片地址")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")


class upload_file(Model):
    file_name = fields.CharField(max_length=255, description="文件名称")
    file_path = fields.TextField(description="文件地址")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")


class airtest_img(Model):
    file_name = fields.CharField(max_length=255, description="图片名称")
    file_path = fields.TextField(description="图片地址")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    menu = fields.ForeignKeyField("models.App_menu", description="所属菜单", null=True)

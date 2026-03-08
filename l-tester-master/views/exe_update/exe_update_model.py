from tortoise import fields, Model


class exe_update_version(Model):
    name = fields.CharField(max_length=255, description="名称")
    version = fields.CharField(max_length=255, description="版本号")
    url = fields.CharField(max_length=255, description="下载地址")
    size = fields.IntField(description="大小")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")

from tortoise import fields, Model


class Call_list(Model):
    success_list = fields.JSONField(description="拨通列表")
    create_time = fields.DatetimeField(auto_now_add=True, description="拨打电话时间")

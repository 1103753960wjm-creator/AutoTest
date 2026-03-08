from tortoise import fields, Model

class Scheduler_Task(Model):
    name = fields.CharField(max_length=255, description="任务名称")
    type = fields.IntField(description="任务类型")
    status = fields.IntField(description="任务状态")
    script = fields.JSONField(description="任务脚本", default={})
    time = fields.JSONField(description="任务时间", default={})
    notice = fields.JSONField(description="推送配置", default={})
    user = fields.ForeignKeyField("models.User_info")
    description = fields.CharField(max_length=255, description="任务描述", null=True)
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")

class Msg_Notice(Model):
    name = fields.CharField(max_length=255, description="通知名称")
    type = fields.IntField(description="通知类型")
    value = fields.CharField(max_length=255, description="地址")
    status = fields.IntField(description="通知状态")
    script = fields.JSONField(description="通知脚本", default={})
    user= fields.ForeignKeyField("models.User_info")
    description = fields.CharField(max_length=255, description="任务描述", null=True)
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")
from tortoise import fields, Model


class App_menu(Model):
    name = fields.CharField(max_length=255, description="名称", unique=True)
    pid = fields.IntField(description="父id")
    type = fields.IntField(description="类型")
    user = fields.ForeignKeyField("models.User_info")


class App_script(Model):
    script = fields.JSONField(description="脚本")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")
    menu = fields.ForeignKeyField("models.App_menu")
    user = fields.ForeignKeyField("models.User_info")


class App_result(Model):
    device = fields.CharField(max_length=255, description="设备")
    result_id = fields.CharField(max_length=255, description="结果id")
    name = fields.CharField(max_length=255, description="脚本名称")
    status = fields.IntField(description="状态")  # 0：失败，1：成功
    log = fields.TextField(description="详情")
    assert_value = fields.JSONField(description="断言详情")
    before_img = fields.TextField(description="执行前截图地址")
    after_img = fields.TextField(description="执行后截图地址")
    video = fields.TextField(description="视频地址")
    performance = fields.JSONField(description="实时性能")
    menu = fields.ForeignKeyField("models.App_menu")
    create_time = fields.DatetimeField(auto_now_add=True, description="执行时间")


class App_result_list(Model):
    task_name = fields.CharField(max_length=255, description="任务名称")
    device_list = fields.JSONField(description="设备列表")
    result_id = fields.CharField(max_length=255, description="结果id", unique=True)
    script_list = fields.JSONField(description="脚本列表")
    script_status = fields.JSONField(description="脚本执行情况")
    start_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    end_time = fields.DatetimeField(null=True, description="更新时间")
    user = fields.ForeignKeyField("models.User_info", default=1)


class App_device(Model):
    device_name = fields.CharField(max_length=255, description="设备名称")
    device_id = fields.CharField(max_length=255, description="设备id")
    device_status = fields.IntField(description="设备状态")
    device_type = fields.CharField(max_length=255, description="设备类型")
    device_version = fields.CharField(max_length=255, description="设备版本")
    device_info = fields.JSONField(description="设备信息")
    file_path = fields.TextField(description="设备图片")
    device_description = fields.TextField(description="设备描述", null=True)
    user = fields.ForeignKeyField("models.User_info")


class App_device_log(Model):
    device = fields.ForeignKeyField("models.App_device")
    user = fields.ForeignKeyField("models.User_info")
    start_time = fields.DatetimeField(auto_now_add=True, description="开始时间")
    end_time = fields.DatetimeField(null=True, description="结束时间")


class App_device_install(Model):
    apk_name = fields.TextField(description="文件名称")
    apk_path = fields.TextField(description="文件地址")
    device = fields.ForeignKeyField("models.App_device")
    user = fields.ForeignKeyField("models.User_info")
    create_time = fields.DatetimeField(auto_now_add=True, description="安装时间")


class App_device_log_list(Model):
    id = fields.IntField(description="id", primary_key=True)
    name = fields.CharField(max_length=255, description="名称")
    together_id = fields.IntField(description="关联id")

    class Meta:
        unique_together = (("name", "together_id"),)

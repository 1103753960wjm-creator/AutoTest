from tortoise import fields, Model


class Web_menu(Model):
    name = fields.CharField(max_length=255, description="名称", unique=True)
    pid = fields.IntField(description="父id")
    type = fields.IntField(description="类型")
    user = fields.ForeignKeyField("models.User_info")

class Web_script(Model):
    script = fields.JSONField(description="脚本")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")
    menu = fields.ForeignKeyField("models.Web_menu")
    user = fields.ForeignKeyField("models.User_info")

class Web_element_menu(Model):
    name = fields.CharField(max_length=255, description="名称", unique=True)
    pid = fields.IntField(description="父id")
    type = fields.IntField(description="类型")
    element = fields.ForeignKeyField("models.Web_element", null=True)
    user = fields.ForeignKeyField("models.User_info")

class Web_element(Model):
    name = fields.CharField(max_length=255, description="名称")
    element = fields.JSONField(description="元素内容")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")
    user = fields.ForeignKeyField("models.User_info")
    menu_id = fields.IntField(description="菜单id", null=True)

class Web_group(Model):
    name = fields.CharField(max_length=255, description="名称", unique=True)
    script = fields.JSONField(description="脚本", default=[])
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")
    user = fields.ForeignKeyField("models.User_info")
    description = fields.CharField(max_length=255, description="描述")

class Web_result_list(Model):
    task_name = fields.CharField(max_length=255, description="任务名称")
    result_id = fields.CharField(max_length=255, description="结果id")
    script_list = fields.JSONField(description="脚本列表")
    browser_list = fields.JSONField(description="浏览器列表")
    result = fields.JSONField(description="结果")
    start_time = fields.DatetimeField(auto_now_add=True, description="开始时间")
    end_time = fields.DatetimeField(null=True, description="结束时间")
    user = fields.ForeignKeyField("models.User_info")
    status = fields.IntField(description="状态", default=1)

class Web_result_detail(Model):
    name = fields.CharField(max_length=255, description="名称")
    result_id = fields.CharField(max_length=255, description="结果id")
    browser = fields.CharField(max_length=255, description="浏览器")
    log = fields.TextField(description="执行日志")
    status = fields.IntField(description="状态")
    before_img = fields.CharField(max_length=255, description="执行前截图", null=True)
    after_img = fields.CharField(max_length=255, description="执行后截图", null=True)
    video = fields.CharField(max_length=255, description="视频", null=True)
    trace = fields.CharField(max_length=255, description="trace", null=True)
    assert_result = fields.JSONField(description="断言结果")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    menu = fields.ForeignKeyField("models.Web_menu", null=True)

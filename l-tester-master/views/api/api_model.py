from tortoise import fields, Model

class Api_project(Model):
    name = fields.CharField(max_length=255, description="项目名称")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")
    img = fields.CharField(max_length=255, description="项目图片")
    user = fields.ForeignKeyField("models.User_info")

class Api_service(Model):
    name = fields.CharField(max_length=255, description="服务名称")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")
    api_project = fields.ForeignKeyField("models.Api_project")
    img = fields.CharField(max_length=255, description="服务图片")
    user = fields.ForeignKeyField("models.User_info")

class Api_envs(Model):
    name = fields.CharField(max_length=255, description="环境名称")
    config = fields.JSONField(description="环境配置", default=[])
    variable = fields.JSONField(description="环境变量", default=[])
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")
    user = fields.ForeignKeyField("models.User_info")

class Api_var(Model):
    name = fields.CharField(max_length=255, description="变量名称")
    value = fields.CharField(max_length=255, description="变量值")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")
    user = fields.ForeignKeyField("models.User_info")

class Api(Model):
    url = fields.CharField(max_length=255, description="接口地址")
    req = fields.JSONField(description="请求参数", default={})
    document = fields.JSONField( description="接口描述", default={})
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")
    api_service = fields.ForeignKeyField("models.Api_service")
    user = fields.ForeignKeyField("models.User_info")

class Api_menu(Model):
    name = fields.CharField(max_length=255, description="菜单名称")
    type = fields.IntField(description="菜单类型")
    pid = fields.IntField(description="父级菜单")
    api = fields.ForeignKeyField("models.Api", null=True)
    api_service = fields.ForeignKeyField("models.Api_service")
    status = fields.IntField(description="菜单状态")
    user = fields.ForeignKeyField("models.User_info")

class Api_result(Model):
    req = fields.JSONField(description="请求参数", default={})
    res = fields.JSONField(description="响应结果", default={})
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    api = fields.ForeignKeyField("models.Api")
    user= fields.ForeignKeyField("models.User_info")

class Api_edit(Model):
    edit = fields.JSONField(description="请求参数", default={})
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    api = fields.ForeignKeyField("models.Api")
    user = fields.ForeignKeyField("models.User_info")

class Api_update(Model):
    req = fields.JSONField(description="请求参数", default={})
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    api = fields.ForeignKeyField("models.Api")
    api_service = fields.ForeignKeyField("models.Api_service")
    user= fields.ForeignKeyField("models.User_info")

class Api_delete(Model):
    api = fields.ForeignKeyField("models.Api")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    user= fields.ForeignKeyField("models.User_info")

class Api_function(Model):
    name = fields.CharField(max_length=255, description="公共函数名称")
    description = fields.CharField(max_length=255, description="公共函数描述")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")
    user= fields.ForeignKeyField("models.User_info")

class Api_db(Model):
    name = fields.CharField(max_length=255, description="数据库名称")
    config = fields.JSONField(description="数据库配置", default={})
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")
    user= fields.ForeignKeyField("models.User_info")

class Api_code(Model):
    name = fields.CharField(max_length=255, description="代码名称")
    code = fields.CharField(max_length=255, description="代码内容")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    user = fields.ForeignKeyField("models.User_info")

class Api_params(Model):
    name = fields.CharField(max_length=255, description="参数名称")
    value = fields.JSONField(description="参数值", default={})
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    user = fields.ForeignKeyField("models.User_info")

class Api_script(Model):
    name = fields.CharField(max_length=255, description="脚本名称")
    type = fields.IntField(description="脚本类型", default=1)
    script = fields.JSONField(description="脚本内容")
    config = fields.JSONField(description="脚本配置", default={})
    description = fields.CharField(max_length=255, description="脚本描述", default="")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")
    user = fields.ForeignKeyField("models.User_info")

class Api_script_result_list(Model):
    result_id = fields.BigIntField(description="结果id")
    config = fields.JSONField(description="配置", default={})
    name = fields.CharField(max_length=255, description="结果名称")
    script = fields.JSONField(description="测试脚本", default={})
    result = fields.JSONField(description="脚本结果", default=[])
    start_time = fields.DatetimeField(auto_now_add=True, description="开始时间")
    end_time = fields.DatetimeField(auto_now_add=True, description="结束时间", null=True)
    user = fields.ForeignKeyField("models.User_info")

class Api_script_result(Model):
    name = fields.CharField(max_length=255, description="名称")
    uuid = fields.CharField(max_length=255, description="uuid", null=True)
    menu_id = fields.CharField(max_length=255, description="菜单id")
    result_id = fields.BigIntField(description="结果id")
    status = fields.IntField(description="状态", default=1)
    req = fields.JSONField(description="请求", default={})
    res = fields.JSONField(description="结果", default={})
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
from tortoise import fields, Model

class User_info(Model):
    """用户表."""

    id = fields.IntField(pk=True, description="用户ID")
    username = fields.CharField(max_length=14, description="用户名")
    password = fields.CharField(max_length=255, description="用户密码")
    account = fields.CharField(max_length=255, description="账户")
    token = fields.CharField(max_length=255, description="token")
    token_time = fields.DatetimeField(auto_now_add=True, description="token失效时间")
    avatar = fields.CharField(max_length=255, description="")
    phone = fields.CharField(max_length=255, description="手机号")
    email = fields.CharField(max_length=255, description="邮箱")
    status = fields.CharField(max_length=1, description="状态", default=1)
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")

class User_info_log(Model):
    """用户操作日志表."""
    user = user = fields.ForeignKeyField("models.User_info")
    log_ip = fields.CharField(max_length=255, description="操作IP")
    create_time = fields.DatetimeField(auto_now_add=True, description="操作时间")
    log_api = fields.CharField(max_length=255, description="操作接口")
    log_content = fields.JSONField(description="操作内容")
    log_status = fields.CharField(max_length=10, description="操作状态", default=1)
    log_result = fields.JSONField(description="操作结果")

class User_info_login_log(Model):
    """用户登录日志表."""
    login_user = fields.CharField(max_length=255, description="登录用户")
    create_time = fields.DatetimeField(auto_now_add=True, description="登录时间")
    login_ip = fields.CharField(max_length=255, description="登录IP")
    login_result = fields.TextField(description="登录结果")

class Role(Model):
    """角色表."""
    name = fields.CharField(max_length=255, description="角色名称")
    user = fields.ForeignKeyField("models.User_info")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")

class Permission(Model):
    name = fields.CharField(max_length=255, description="权限名称")
    type = fields.IntField(description="权限类型")
    url = fields.CharField(max_length=255, description="权限url", null=True)
    pid = fields.IntField(description="父级id")
    user = fields.ForeignKeyField("models.User_info")

class Role_user(Model):
    role = fields.ForeignKeyField("models.Role")
    user = fields.ForeignKeyField("models.User_info")

class Role_permission(Model):
    role = fields.ForeignKeyField("models.Role")
    permission = fields.ForeignKeyField("models.Permission")
from tortoise import Model, fields


class Requirement(Model):
    title = fields.CharField(max_length=255, description="需求标题")
    source_type = fields.CharField(max_length=64, description="来源类型")
    source_content = fields.TextField(description="原始需求内容")
    parsed_content = fields.JSONField(description="需求摘要", default=[])
    status = fields.CharField(max_length=32, description="需求状态", default="reviewed")
    version = fields.IntField(description="版本号", default=1)
    user = fields.ForeignKeyField("models.User_info")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")


class Testcase_generation_job(Model):
    requirement = fields.ForeignKeyField("models.Requirement")
    source_type = fields.CharField(max_length=64, description="来源类型")
    source_id = fields.IntField(description="来源id")
    requested_mode = fields.CharField(max_length=32, description="请求模式", default="none")
    effective_mode = fields.CharField(max_length=32, description="生效模式", default="none")
    provider_name = fields.CharField(max_length=255, description="provider名称", default="template_rules")
    prompt_version = fields.CharField(max_length=64, description="prompt版本", default="m2-phase1")
    job_status = fields.CharField(max_length=32, description="任务状态", default="saved")
    summary = fields.JSONField(description="需求摘要", default=[])
    error_message = fields.TextField(description="错误信息", null=True)
    user = fields.ForeignKeyField("models.User_info")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")

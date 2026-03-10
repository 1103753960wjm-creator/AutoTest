from tortoise import Model, fields


class Automation_draft(Model):
    testcase = fields.ForeignKeyField("models.Testcase")
    requirement = fields.ForeignKeyField("models.Requirement")
    target_type = fields.CharField(max_length=32, description="目标类型")
    requested_mode = fields.CharField(
        max_length=32, description="请求模式", default="none"
    )
    effective_mode = fields.CharField(
        max_length=32, description="生效模式", default="none"
    )
    provider_name = fields.CharField(
        max_length=255, description="provider名称", default="template_rules"
    )
    draft_payload = fields.JSONField(description="自动化草稿内容", default={})
    warnings = fields.JSONField(description="生成告警", default=[])
    save_status = fields.CharField(
        max_length=32, description="保存状态", default="draft"
    )
    target_asset_id = fields.IntField(description="目标资产编号", null=True)
    target_menu_id = fields.IntField(description="目标菜单编号", null=True)
    user = fields.ForeignKeyField("models.User_info")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")

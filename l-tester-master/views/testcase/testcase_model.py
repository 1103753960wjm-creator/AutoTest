from tortoise import Model, fields


class Testcase(Model):
    requirement = fields.ForeignKeyField("models.Requirement")
    generation_job = fields.ForeignKeyField("models.Testcase_generation_job")
    source_case_id = fields.CharField(max_length=64, description="来源用例编号", null=True)
    title = fields.CharField(max_length=255, description="用例标题")
    priority = fields.CharField(max_length=32, description="优先级", default="P2")
    module = fields.CharField(max_length=128, description="所属模块", default="")
    category = fields.CharField(max_length=64, description="用例分类", default="general")
    preconditions = fields.JSONField(description="前置条件", default=[])
    steps = fields.JSONField(description="测试步骤", default=[])
    expected_results = fields.JSONField(description="预期结果", default=[])
    target_type = fields.CharField(max_length=32, description="目标类型", default="general")
    automatable = fields.BooleanField(description="是否可自动化", default=False)
    review_status = fields.CharField(max_length=32, description="审核状态", default="approved")
    version = fields.IntField(description="版本号", default=1)
    user = fields.ForeignKeyField("models.User_info")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")

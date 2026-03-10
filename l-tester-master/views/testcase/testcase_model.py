from tortoise import Model, fields


class Testcase(Model):
    __test__ = False

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
    latest_review_comment = fields.TextField(description="最新审核意见", default="")
    latest_review_reason_type = fields.CharField(
        max_length=64, description="最新审核原因类型", default=""
    )
    latest_review_time = fields.DatetimeField(description="最新审核时间", null=True)
    version = fields.IntField(description="版本号", default=1)
    user = fields.ForeignKeyField("models.User_info")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now_add=True, description="更新时间")


class Testcase_revision(Model):
    __test__ = False

    testcase = fields.ForeignKeyField("models.Testcase")
    version = fields.IntField(description="版本号")
    snapshot = fields.JSONField(description="版本快照", default={})
    edit_reason = fields.CharField(max_length=255, description="编辑原因", default="手工编辑")
    user = fields.ForeignKeyField("models.User_info")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")


class Testcase_review_log(Model):
    __test__ = False

    testcase = fields.ForeignKeyField("models.Testcase")
    from_status = fields.CharField(max_length=32, description="变更前状态", default="")
    to_status = fields.CharField(max_length=32, description="变更后状态", default="")
    review_comment = fields.TextField(description="审核意见", default="")
    review_reason_type = fields.CharField(
        max_length=64, description="审核原因类型", default=""
    )
    user = fields.ForeignKeyField("models.User_info")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")


class Testcase_tag(Model):
    __test__ = False

    name = fields.CharField(max_length=64, description="标签名称")
    user = fields.ForeignKeyField("models.User_info")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "testcase_tag"
        unique_together = (("name", "user"),)


class Testcase_tag_rel(Model):
    __test__ = False

    testcase = fields.ForeignKeyField("models.Testcase")
    tag = fields.ForeignKeyField("models.Testcase_tag")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "testcase_tag_rel"
        unique_together = (("testcase", "tag"),)

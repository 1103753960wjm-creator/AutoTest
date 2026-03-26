import re

from rest_framework import serializers
from .result_status import get_result_status_summary

from .models import (
    RequirementDocument,
    RequirementAnalysis,
    BusinessRequirement,
    GeneratedTestCase,
    AnalysisTask,
    AIModelConfig,
    PromptConfig,
    TestCaseGenerationTask,
    TaskAutoReviewRecord,
    GenerationConfig,
)


def _parse_generated_results(content):
    if not content:
        return []

    clean_content = re.sub(r"\*\*([^*]+)\*\*", r"\1", content)
    lines = [line.strip() for line in clean_content.split("\n") if line.strip()]
    table_rows = []

    for line in lines:
        if "|" in line and not line.startswith("|-"):
            columns = [cell.strip() for cell in line.split("|") if cell.strip()]
            if len(columns) > 1:
                table_rows.append(columns)

    if len(table_rows) > 1:
        headers = [header.lower() for header in table_rows[0]]
        results = []
        for index, row in enumerate(table_rows[1:], start=1):
            item = {
                "index": index,
                "case_id": "",
                "scenario": "",
                "precondition": "",
                "steps": "",
                "expected": "",
                "priority": "P2",
            }
            for col_index, header in enumerate(headers):
                value = row[col_index] if col_index < len(row) else ""
                value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
                if "用例" in header or header == "id":
                    item["case_id"] = value
                elif "场景" in header or "目标" in header or "标题" in header:
                    item["scenario"] = value
                elif "前置" in header:
                    item["precondition"] = value
                elif "步骤" in header and "预期" not in header:
                    item["steps"] = value
                elif "预期" in header or "结果" in header:
                    item["expected"] = value
                elif "优先级" in header or header == "priority":
                    item["priority"] = value or "P2"
            if item["scenario"] or item["case_id"]:
                results.append(item)
        return results

    results = []
    current_case = None
    for line in lines:
        if line.startswith(("1.", "2.", "3.", "4.", "5.")) or "测试用例" in line or "Test Case" in line:
            if current_case:
                results.append(current_case)
            current_case = {
                "index": len(results) + 1,
                "case_id": f"TC{len(results) + 1:03d}",
                "scenario": re.sub(r"^(\d+\.|测试用例[:：]?\s*|Test Case[:：]?\s*)", "", line).strip(),
                "precondition": "",
                "steps": "",
                "expected": "",
                "priority": "P2",
            }
        elif current_case and ("前置条件" in line or "前提" in line):
            current_case["precondition"] = re.sub(r".*?[:：]\s*", "", line).strip()
        elif current_case and ("测试步骤" in line or "操作步骤" in line or "步骤" in line):
            current_case["steps"] = re.sub(r".*?[:：]\s*", "", line).strip()
        elif current_case and ("预期结果" in line or "Expected" in line):
            current_case["expected"] = re.sub(r".*?[:：]\s*", "", line).strip()
        elif current_case and "优先级" in line:
            current_case["priority"] = re.sub(r".*?[:：]\s*", "", line).strip() or "P2"

    if current_case:
        results.append(current_case)

    return results


def _build_active_config_source_summary():
    writer_model = AIModelConfig.objects.filter(role="writer", is_active=True).first()
    reviewer_model = AIModelConfig.objects.filter(role="reviewer", is_active=True).first()
    writer_prompt = PromptConfig.get_active_config("writer")
    reviewer_prompt = PromptConfig.get_active_config("reviewer")
    generation_config = GenerationConfig.get_active_config()

    is_ready = bool(writer_model and writer_prompt and generation_config)

    return {
        "is_ready": is_ready,
        "label": "当前活跃配置已就绪" if is_ready else "当前活跃配置待补齐",
        "detail": "当前页面展示的是活跃配置推断摘要，任务页若已持有模型或提示词外键，应优先展示任务执行时使用信息。",
        "writer_model": writer_model.name if writer_model else "",
        "reviewer_model": reviewer_model.name if reviewer_model else "",
        "writer_prompt": writer_prompt.name if writer_prompt else "",
        "reviewer_prompt": reviewer_prompt.name if reviewer_prompt else "",
        "generation_config": generation_config.name if generation_config else "",
    }


def _build_generation_config_summary(config):
    return {
        "name": config.name if config else "",
        "is_inferred": True,
        "source_type": "active_config_inference",
        "label": f"当前活跃配置：{config.name}" if config else "未找到当前活跃生成配置",
        "detail": "当前任务模型未持久化任务级生成配置，本轮仅展示当前活跃配置推断摘要，不等于任务执行真实快照。",
        "executed_with_snapshot": False,
    }


def _build_task_failure_summary(obj):
    if not obj.error_message:
        return {
            "has_error": False,
            "stage": "",
            "label": "当前未记录失败信息",
            "detail": "本轮仅提供轻量失败摘要位，后续再补完整调用留痕与阶段化错误追踪。",
        }

    stage = "task_runtime"
    if obj.status == "failed":
        if obj.review_feedback and not obj.final_test_cases:
            stage = "review_or_revision"
        elif obj.generated_test_cases and not obj.review_feedback:
            stage = "review_entry"
        elif not obj.generated_test_cases:
            stage = "generation_entry"

    return {
        "has_error": True,
        "stage": stage,
        "label": "任务最近一次执行失败",
        "detail": obj.error_message,
    }


def _get_latest_auto_review_record(obj):
    prefetched_records = getattr(obj, "_prefetched_objects_cache", {}).get("auto_review_records")
    if prefetched_records:
        return prefetched_records[0]
    return obj.auto_review_records.order_by("-created_at", "-id").first()


def _build_auto_review_summary(obj):
    record = _get_latest_auto_review_record(obj)
    if not record:
        return {
            "has_record": False,
            "review_id": None,
            "status": "not_triggered",
            "label": "未触发自动评审",
            "detail": "当前生成任务尚未触发自动 AI 评审记录。",
            "entry_path": f"/ai-generation/reviews/ai-auto?taskId={obj.task_id}",
            "created_at": None,
        }

    summary_map = {
        "reviewing": ("自动评审进行中", "当前任务的自动 AI 评审仍在执行，可进入统一入口继续查看。"),
        "completed": ("已生成 AI 自动评审", "来自当前生成任务的自动评审记录，可进入统一 AI 评审入口查看。"),
        "failed": ("自动评审失败", record.failure_message or "自动评审执行失败，可进入统一入口查看失败信息。"),
        "cancelled": ("自动评审已取消", "自动评审在生成链执行过程中被取消，可进入统一入口查看保留内容。"),
    }
    label, detail = summary_map.get(
        record.review_status,
        ("自动评审状态未知", "当前自动评审记录已存在，但状态未匹配固定枚举。"),
    )
    return {
        "has_record": True,
        "review_id": record.id,
        "status": record.review_status,
        "label": label,
        "detail": detail,
        "entry_path": f"/ai-generation/reviews/ai-auto?taskId={obj.task_id}",
        "created_at": record.created_at,
    }


class RequirementDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.username", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    document_type_display = serializers.CharField(source="get_document_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = RequirementDocument
        fields = [
            "id",
            "title",
            "file",
            "file_url",
            "document_type",
            "document_type_display",
            "status",
            "status_display",
            "uploaded_by",
            "uploaded_by_name",
            "project",
            "project_name",
            "created_at",
            "updated_at",
            "file_size",
            "extracted_text",
        ]
        read_only_fields = ["uploaded_by", "file_size", "extracted_text"]

    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None


class BusinessRequirementSerializer(serializers.ModelSerializer):
    requirement_type_display = serializers.CharField(source="get_requirement_type_display", read_only=True)
    requirement_level_display = serializers.CharField(source="get_requirement_level_display", read_only=True)
    parent_requirement_name = serializers.CharField(source="parent_requirement.requirement_name", read_only=True)

    class Meta:
        model = BusinessRequirement
        fields = [
            "id",
            "requirement_id",
            "requirement_name",
            "requirement_type",
            "requirement_type_display",
            "parent_requirement",
            "parent_requirement_name",
            "module",
            "requirement_level",
            "requirement_level_display",
            "reviewer",
            "estimated_hours",
            "description",
            "acceptance_criteria",
            "created_at",
            "updated_at",
        ]


class RequirementAnalysisSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source="document.title", read_only=True)
    document_id = serializers.IntegerField(source="document.id", read_only=True)
    project_id = serializers.IntegerField(source="document.project.id", read_only=True)
    project_name = serializers.CharField(source="document.project.name", read_only=True)
    requirements = BusinessRequirementSerializer(many=True, read_only=True)
    input_content_summary = serializers.SerializerMethodField()
    analysis_status = serializers.CharField(source="document.status", read_only=True)
    last_analysis_at = serializers.DateTimeField(source="updated_at", read_only=True)
    config_source_summary = serializers.SerializerMethodField()
    task_entry_summary = serializers.SerializerMethodField()

    class Meta:
        model = RequirementAnalysis
        fields = [
            "id",
            "document_id",
            "document_title",
            "analysis_report",
            "requirements_count",
            "analysis_time",
            "created_at",
            "updated_at",
            "requirements",
            "project_id",
            "project_name",
            "input_content_summary",
            "analysis_status",
            "last_analysis_at",
            "config_source_summary",
            "task_entry_summary",
        ]

    def get_input_content_summary(self, obj):
        document = obj.document
        return {
            "title": document.title,
            "document_type": document.document_type,
            "document_type_display": document.get_document_type_display(),
            "file_size": document.file_size,
            "text_length": len(document.extracted_text or ""),
            "label": f"{document.get_document_type_display()} / {document.title}",
        }

    def get_config_source_summary(self, obj):
        return _build_active_config_source_summary()

    def get_task_entry_summary(self, obj):
        return {
            "is_inferred": True,
            "label": "可从当前分析上下文继续发起生成任务",
            "detail": "当前分析对象与生成任务尚未形成 analysis 外键绑定，本轮仅保留“来源分析说明”语义位。",
        }


class GeneratedTestCaseSerializer(serializers.ModelSerializer):
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    requirement_name = serializers.CharField(source="requirement.requirement_name", read_only=True)
    requirement_id_display = serializers.CharField(source="requirement.requirement_id", read_only=True)
    project_id = serializers.IntegerField(source="requirement.analysis.document.project.id", read_only=True)
    project_name = serializers.CharField(source="requirement.analysis.document.project.name", read_only=True)
    source_task_id = serializers.SerializerMethodField()
    save_status_summary = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedTestCase
        fields = [
            "id",
            "case_id",
            "title",
            "priority",
            "priority_display",
            "precondition",
            "test_steps",
            "expected_result",
            "status",
            "status_display",
            "generated_by_ai",
            "reviewed_by_ai",
            "review_comments",
            "requirement",
            "requirement_name",
            "requirement_id_display",
            "project_id",
            "project_name",
            "source_task_id",
            "save_status_summary",
            "created_at",
            "updated_at",
        ]

    def get_source_task_id(self, obj):
        return ""

    def get_save_status_summary(self, obj):
        return {
            "is_saved_to_testcases": obj.status == "adopted",
            "label": "已保存为测试用例" if obj.status == "adopted" else "尚未保存为正式测试用例",
        }


class AnalysisTaskSerializer(serializers.ModelSerializer):
    task_type_display = serializers.CharField(source="get_task_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    document_title = serializers.CharField(source="document.title", read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisTask
        fields = [
            "id",
            "task_id",
            "task_type",
            "task_type_display",
            "document",
            "document_title",
            "status",
            "status_display",
            "progress",
            "result",
            "error_message",
            "started_at",
            "completed_at",
            "created_at",
            "duration",
        ]
        read_only_fields = ["task_id", "result", "error_message", "started_at", "completed_at"]

    def get_duration(self, obj):
        if obj.started_at and obj.completed_at:
            return (obj.completed_at - obj.started_at).total_seconds()
        return None


class DocumentUploadSerializer(serializers.ModelSerializer):
    """文档上传专用序列化器"""

    class Meta:
        model = RequirementDocument
        fields = ["id", "title", "file", "project"]

    def create(self, validated_data):
        user = self.context["request"].user
        if user.is_authenticated:
            validated_data["uploaded_by"] = user
        else:
            from apps.users.models import User

            default_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
            validated_data["uploaded_by"] = default_user

        file = validated_data["file"]
        if file.name.lower().endswith(".pdf"):
            validated_data["document_type"] = "pdf"
        elif file.name.lower().endswith((".doc", ".docx")):
            validated_data["document_type"] = "docx"
        elif file.name.lower().endswith(".txt"):
            validated_data["document_type"] = "txt"
        elif file.name.lower().endswith(".md"):
            validated_data["document_type"] = "md"

        validated_data["file_size"] = file.size
        return super().create(validated_data)


class TestCaseGenerationRequestSerializer(serializers.Serializer):
    """旧的测试用例生成请求序列化器"""

    requirement_ids = serializers.ListField(child=serializers.IntegerField(), help_text="需求 ID 列表")
    test_level = serializers.ChoiceField(
        choices=[
            ("unit", "单元测试"),
            ("integration", "集成测试"),
            ("system", "系统测试"),
            ("acceptance", "验收测试"),
        ],
        default="system",
        help_text="测试级别",
    )
    test_priority = serializers.ChoiceField(
        choices=[("P0", "最高优先级"), ("P1", "高优先级"), ("P2", "中优先级"), ("P3", "低优先级")],
        default="P1",
        help_text="测试优先级",
    )
    test_case_count = serializers.IntegerField(min_value=1, max_value=200, default=50, help_text="生成测试用例数量")


class TestCaseReviewRequestSerializer(serializers.Serializer):
    """测试用例评审请求序列化器"""

    test_case_ids = serializers.ListField(child=serializers.IntegerField(), help_text="测试用例 ID 列表")
    review_criteria = serializers.CharField(
        max_length=500,
        default="检查测试用例的完整性、准确性和可执行性",
        help_text="评审标准",
    )


class AIModelConfigSerializer(serializers.ModelSerializer):
    """AI 模型配置序列化器"""

    model_type_display = serializers.CharField(source="get_model_type_display", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    api_key_masked = serializers.SerializerMethodField(read_only=True)
    usage_scope_summary = serializers.SerializerMethodField(read_only=True)
    activation_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AIModelConfig
        fields = [
            "id",
            "name",
            "model_type",
            "model_type_display",
            "role",
            "role_display",
            "api_key",
            "api_key_masked",
            "base_url",
            "model_name",
            "max_tokens",
            "temperature",
            "top_p",
            "is_active",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "usage_scope_summary",
            "activation_summary",
        ]
        read_only_fields = ["created_by", "created_by_name"]
        extra_kwargs = {"api_key": {"write_only": True}}

    def get_api_key_masked(self, obj):
        if obj.api_key:
            if len(obj.api_key) > 7:
                return f"{obj.api_key[:3]}{'*' * (len(obj.api_key) - 7)}{obj.api_key[-4:]}"
            return "*" * len(obj.api_key)
        return ""

    def get_usage_scope_summary(self, obj):
        role_label = "用例编写模型来源" if obj.role == "writer" else "用例评审模型来源"
        return {
            "role": obj.role,
            "label": role_label,
            "detail": "当前配置页承担生成链上游来源层职责，分析页与任务页会消费其活跃配置摘要。",
        }

    def get_activation_summary(self, obj):
        return {
            "is_active": obj.is_active,
            "label": "当前活跃配置" if obj.is_active else "非活跃配置",
            "detail": "只有活跃配置会被 RequirementAnalysisView 作为当前活跃配置推断摘要消费。",
        }

    def create(self, validated_data):
        user = self.context["request"].user
        if user.is_authenticated:
            validated_data["created_by"] = user
        else:
            from apps.users.models import User

            default_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
            validated_data["created_by"] = default_user
        return super().create(validated_data)


class PromptConfigSerializer(serializers.ModelSerializer):
    """提示词配置序列化器"""

    prompt_type_display = serializers.CharField(source="get_prompt_type_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    usage_scope_summary = serializers.SerializerMethodField(read_only=True)
    activation_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PromptConfig
        fields = [
            "id",
            "name",
            "prompt_type",
            "prompt_type_display",
            "content",
            "is_active",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "usage_scope_summary",
            "activation_summary",
        ]
        read_only_fields = ["created_by", "created_by_name"]

    def get_usage_scope_summary(self, obj):
        role_label = "用例编写 Prompt 来源" if obj.prompt_type == "writer" else "用例评审 Prompt 来源"
        return {
            "prompt_type": obj.prompt_type,
            "label": role_label,
            "detail": "提示词配置在 2.2 第一阶段作为生成链上游来源层展示，不在本轮重构其后台流程。",
        }

    def get_activation_summary(self, obj):
        return {
            "is_active": obj.is_active,
            "label": "当前活跃提示词" if obj.is_active else "非活跃提示词",
            "detail": "任务若持有提示词外键，应优先展示任务执行时使用信息。",
        }

    def create(self, validated_data):
        user = self.context["request"].user
        if user.is_authenticated:
            validated_data["created_by"] = user
        else:
            from apps.users.models import User

            default_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
            validated_data["created_by"] = default_user
        return super().create(validated_data)


class TestCaseGenerationTaskSerializer(serializers.ModelSerializer):
    """测试用例生成任务序列化器"""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    writer_model_name = serializers.CharField(source="writer_model_config.name", read_only=True)
    reviewer_model_name = serializers.CharField(source="reviewer_model_config.name", read_only=True)
    writer_prompt_name = serializers.CharField(source="writer_prompt_config.name", read_only=True)
    reviewer_prompt_name = serializers.CharField(source="reviewer_prompt_config.name", read_only=True)
    generation_config_summary = serializers.SerializerMethodField()
    result_count = serializers.SerializerMethodField()
    save_status_summary = serializers.SerializerMethodField()
    processing_status_summary = serializers.SerializerMethodField()
    generated_results_preview = serializers.SerializerMethodField()
    source_summary = serializers.SerializerMethodField()
    source_analysis_summary = serializers.SerializerMethodField()
    model_source_summary = serializers.SerializerMethodField()
    prompt_source_summary = serializers.SerializerMethodField()
    failure_summary = serializers.SerializerMethodField()
    downstream_summary = serializers.SerializerMethodField()
    auto_review_summary = serializers.SerializerMethodField()

    class Meta:
        model = TestCaseGenerationTask
        fields = [
            "id",
            "task_id",
            "title",
            "requirement_text",
            "status",
            "status_display",
            "progress",
            "output_mode",
            "stream_buffer",
            "last_stream_update",
            "project",
            "project_name",
            "writer_model_config",
            "writer_model_name",
            "reviewer_model_config",
            "reviewer_model_name",
            "writer_prompt_config",
            "writer_prompt_name",
            "reviewer_prompt_config",
            "reviewer_prompt_name",
            "generated_test_cases",
            "review_feedback",
            "final_test_cases",
            "generation_log",
            "error_message",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "completed_at",
            "generation_config_summary",
            "result_count",
            "save_status_summary",
            "processing_status_summary",
            "generated_results_preview",
            "source_summary",
            "source_analysis_summary",
            "model_source_summary",
            "prompt_source_summary",
            "failure_summary",
            "downstream_summary",
            "auto_review_summary",
            "is_saved_to_records",
            "saved_at",
        ]
        read_only_fields = [
            "task_id",
            "status",
            "progress",
            "generated_test_cases",
            "review_feedback",
            "final_test_cases",
            "generation_log",
            "error_message",
            "created_by",
            "completed_at",
        ]

    def get_generation_config_summary(self, obj):
        return _build_generation_config_summary(GenerationConfig.get_active_config())

    def get_result_count(self, obj):
        return len(_parse_generated_results(obj.final_test_cases or obj.generated_test_cases))

    def get_save_status_summary(self, obj):
        return {
            "is_saved": obj.is_saved_to_records,
            "label": "已保存为正式测试用例" if obj.is_saved_to_records else "尚未保存为正式测试用例",
            "saved_at": obj.saved_at,
        }

    def get_processing_status_summary(self, obj):
        return get_result_status_summary(obj)

    def get_generated_results_preview(self, obj):
        return _parse_generated_results(obj.final_test_cases or obj.generated_test_cases)[:3]

    def get_source_summary(self, obj):
        return {
            "project_id": obj.project_id,
            "project_name": obj.project.name if obj.project else "",
            "label": f"来源项目：{obj.project.name}" if obj.project else "来源项目未记录",
            "detail": "生成任务对象承接测试设计项目、需求输入与 AI 配置上下文。",
        }

    def get_source_analysis_summary(self, obj):
        return {
            "is_inferred": True,
            "binding_mode": "analysis_context_only",
            "label": "当前仅记录来源分析上下文摘要",
            "detail": "当前任务模型没有 analysis 外键，本轮只展示“来源分析说明”，不伪装成真实分析对象绑定。",
        }

    def get_model_source_summary(self, obj):
        return {
            "writer_model_name": obj.writer_model_config.name if obj.writer_model_config else "",
            "reviewer_model_name": obj.reviewer_model_config.name if obj.reviewer_model_config else "",
            "label": "任务执行模型信息",
            "detail": "模型信息来自任务对象持有的模型外键，属于任务执行时使用信息。",
        }

    def get_prompt_source_summary(self, obj):
        return {
            "writer_prompt_name": obj.writer_prompt_config.name if obj.writer_prompt_config else "",
            "reviewer_prompt_name": obj.reviewer_prompt_config.name if obj.reviewer_prompt_config else "",
            "label": "任务执行 Prompt 信息",
            "detail": "Prompt 信息来自任务对象持有的提示词外键，属于任务执行时使用信息。",
        }

    def get_failure_summary(self, obj):
        return _build_task_failure_summary(obj)

    def get_downstream_summary(self, obj):
        result_count = self.get_result_count(obj)
        return {
            "result_count": result_count,
            "has_generated_results": result_count > 0,
            "label": "下游入口预留到生成结果页",
            "detail": "2.2 第一阶段仅在任务页预留结果入口位，不在本轮展开结果确认流。",
        }

    def create(self, validated_data):
        import uuid

        user = self.context["request"].user
        if user.is_authenticated:
            validated_data["created_by"] = user
        else:
            from apps.users.models import User

            default_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
            validated_data["created_by"] = default_user

        validated_data["task_id"] = f"TASK_{uuid.uuid4().hex[:8].upper()}"
        return super().create(validated_data)

    def get_auto_review_summary(self, obj):
        return _build_auto_review_summary(obj)


class TestCaseGenerationRequestSerializer(serializers.Serializer):
    """新的测试用例生成请求序列化器"""

    title = serializers.CharField(max_length=200, help_text="任务标题")
    requirement_text = serializers.CharField(help_text="需求描述")
    project = serializers.IntegerField(required=False, allow_null=True, help_text="关联项目 ID")
    use_writer_model = serializers.BooleanField(default=True, help_text="是否使用编写模型")
    use_reviewer_model = serializers.BooleanField(default=True, help_text="是否使用评审模型")


class TaskAutoReviewRecordSerializer(serializers.ModelSerializer):
    """自动 AI 评审记录序列化器"""

    project_name = serializers.CharField(source="project.name", read_only=True)
    task_id = serializers.CharField(source="task.task_id", read_only=True)
    task_title = serializers.CharField(source="task.title", read_only=True)

    class Meta:
        model = TaskAutoReviewRecord
        fields = [
            "id",
            "task",
            "task_id",
            "task_title",
            "project",
            "project_name",
            "review_source",
            "source_stage",
            "review_status",
            "review_summary",
            "review_content",
            "reviewer_model_name",
            "reviewer_prompt_name",
            "result_identity_snapshot",
            "failure_message",
            "created_at",
            "updated_at",
            "completed_at",
        ]
        read_only_fields = fields


class GenerationConfigSerializer(serializers.ModelSerializer):
    """生成行为配置序列化器"""

    default_output_mode_display = serializers.CharField(source="get_default_output_mode_display", read_only=True)
    source_summary = serializers.SerializerMethodField(read_only=True)
    activation_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GenerationConfig
        fields = [
            "id",
            "name",
            "default_output_mode",
            "default_output_mode_display",
            "enable_auto_review",
            "review_timeout",
            "is_active",
            "created_at",
            "updated_at",
            "source_summary",
            "activation_summary",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_source_summary(self, obj):
        return {
            "label": "生成链行为来源",
            "detail": "当前活跃生成配置会被 RequirementAnalysisView 消费，并在 TaskDetail 中以推断摘要展示。",
        }

    def get_activation_summary(self, obj):
        return {
            "is_active": obj.is_active,
            "label": "当前活跃生成配置" if obj.is_active else "非活跃生成配置",
            "detail": "当前系统尚未持久化任务级生成配置快照，活跃配置只可作为推断摘要来源。",
        }

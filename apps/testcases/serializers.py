from rest_framework import serializers
from .models import TestCase, TestCaseStep, TestCaseAttachment, TestCaseComment
from apps.users.serializers import UserSerializer
from apps.versions.serializers import VersionSimpleSerializer


def _extract_ai_source_from_tags(tags):
    if not isinstance(tags, list):
        return None

    for item in tags:
        if not isinstance(item, dict):
            continue
        if item.get('source') != 'ai_generation_task':
            continue
        return item

    return None


def _build_testcase_object_summaries(obj):
    ai_source = _extract_ai_source_from_tags(getattr(obj, 'tags', []))

    if ai_source:
        source_summary = {
            'type': 'ai',
            'label': 'AI 生成',
            'detail': f"来源任务 {ai_source.get('task_id') or '-'}"
        }
        generation_source_summary = {
            'label': '来源于 AI 生成任务',
            'task_id': ai_source.get('task_id') or '',
            'project_id': ai_source.get('project_id'),
            'project_name': ai_source.get('project_name') or '',
            'detail': ai_source.get('source_label') or '由 AI 生成链导入'
        }
    else:
        source_summary = {
            'type': 'unknown',
            'label': '来源未记录',
            'detail': '当前历史数据未稳定记录人工 / AI 来源。'
        }
        generation_source_summary = {
            'label': 'AI 来源待补齐',
            'task_id': '',
            'project_id': None,
            'project_name': '',
            'detail': '后续 AI 生成任务与正式用例的回链将在此处继续收敛。'
        }

    return {
        'source_summary': source_summary,
        'generation_source_summary': generation_source_summary,
        'review_summary': {
            'status': 'pending',
            'label': '评审状态待补齐',
            'detail': '当前测试用例模型未独立持久化评审状态，本轮先保留资产位。'
        },
        'automation_summary': {
            'status': 'pending',
            'label': '待接自动化草稿',
            'detail': '2.3 自动化草稿中心将从测试用例对象继续挂接。'
        }
    }


class TestCaseStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCaseStep
        fields = '__all__'

class TestCaseAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = TestCaseAttachment
        fields = '__all__'

class TestCaseCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = TestCaseComment
        fields = '__all__'

class ProjectSimpleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class TestCaseSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)
    project = ProjectSimpleSerializer(read_only=True)
    versions = VersionSimpleSerializer(many=True, read_only=True)
    step_details = TestCaseStepSerializer(many=True, read_only=True)
    attachments = TestCaseAttachmentSerializer(many=True, read_only=True)
    comments = TestCaseCommentSerializer(many=True, read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    test_type_display = serializers.CharField(source='get_test_type_display', read_only=True)
    source_summary = serializers.SerializerMethodField()
    generation_source_summary = serializers.SerializerMethodField()
    review_summary = serializers.SerializerMethodField()
    automation_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = TestCase
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_source_summary(self, obj):
        return _build_testcase_object_summaries(obj)['source_summary']

    def get_generation_source_summary(self, obj):
        return _build_testcase_object_summaries(obj)['generation_source_summary']

    def get_review_summary(self, obj):
        return _build_testcase_object_summaries(obj)['review_summary']

    def get_automation_summary(self, obj):
        return _build_testcase_object_summaries(obj)['automation_summary']

class TestCaseListSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    assignee = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    versions = serializers.SerializerMethodField()
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    test_type_display = serializers.CharField(source='get_test_type_display', read_only=True)
    source_summary = serializers.SerializerMethodField()
    generation_source_summary = serializers.SerializerMethodField()
    review_summary = serializers.SerializerMethodField()
    automation_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = TestCase
        fields = [
            'id', 'title', 'description', 'preconditions', 'steps', 'expected_result',
            'priority', 'priority_display', 'status', 'status_display',
            'test_type', 'test_type_display',
            'author', 'assignee', 'project', 'versions', 'tags',
            'source_summary', 'generation_source_summary', 'review_summary', 'automation_summary',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_author(self, obj):
        return {'id': obj.author.id, 'username': obj.author.username} if obj.author else None
    
    def get_assignee(self, obj):
        return {'id': obj.assignee.id, 'username': obj.assignee.username} if obj.assignee else None
    
    def get_project(self, obj):
        return {'id': obj.project.id, 'name': obj.project.name} if obj.project else None
    
    def get_versions(self, obj):
        return [{'id': v.id, 'name': v.name, 'is_baseline': v.is_baseline} for v in obj.versions.all()]

    def get_source_summary(self, obj):
        return _build_testcase_object_summaries(obj)['source_summary']

    def get_generation_source_summary(self, obj):
        return _build_testcase_object_summaries(obj)['generation_source_summary']

    def get_review_summary(self, obj):
        return _build_testcase_object_summaries(obj)['review_summary']

    def get_automation_summary(self, obj):
        return _build_testcase_object_summaries(obj)['automation_summary']

class TestCaseCreateSerializer(serializers.ModelSerializer):
    project_id = serializers.IntegerField(required=False, allow_null=True, help_text="项目ID，可选")
    version_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        required=False, 
        allow_empty=True,
        help_text="关联版本ID列表"
    )
    
    class Meta:
        model = TestCase
        fields = [
            'title', 'description', 'preconditions', 'steps', 'expected_result',
            'priority', 'test_type', 'tags', 'project_id', 'version_ids'
        ]
    
    def create(self, validated_data):
        version_ids = validated_data.pop('version_ids', [])
        # project_id会在视图的perform_create中处理
        validated_data.pop('project_id', None)
        
        testcase = super().create(validated_data)
        
        # 设置版本关联
        if version_ids:
            testcase.versions.set(version_ids)
        
        return testcase

class TestCaseUpdateSerializer(serializers.ModelSerializer):
    project_id = serializers.IntegerField(required=False, allow_null=True, help_text="项目ID，可选")
    version_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        required=False, 
        allow_empty=True,
        help_text="关联版本ID列表"
    )
    
    class Meta:
        model = TestCase
        fields = [
            'title', 'description', 'preconditions', 'steps', 'expected_result',
            'priority', 'test_type', 'tags', 'project_id', 'version_ids'
        ]
    
    def update(self, instance, validated_data):
        version_ids = validated_data.pop('version_ids', None)
        # project_id会在视图中处理
        validated_data.pop('project_id', None)
        
        instance = super().update(instance, validated_data)
        
        # 更新版本关联
        if version_ids is not None:
            instance.versions.set(version_ids)

        return instance

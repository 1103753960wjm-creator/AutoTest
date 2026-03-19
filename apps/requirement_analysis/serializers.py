import re
from rest_framework import serializers
from .models import (
    RequirementDocument, RequirementAnalysis, BusinessRequirement,
    GeneratedTestCase, AnalysisTask, AIModelConfig, PromptConfig, TestCaseGenerationTask,
    GenerationConfig
)


def _parse_generated_results(content):
    if not content:
        return []

    clean_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
    lines = [line.strip() for line in clean_content.split('\n') if line.strip()]
    table_rows = []

    for line in lines:
        if '|' in line and not line.startswith('|-'):
            columns = [cell.strip() for cell in line.split('|') if cell.strip()]
            if len(columns) > 1:
                table_rows.append(columns)

    if len(table_rows) > 1:
        headers = [header.lower() for header in table_rows[0]]
        results = []
        for index, row in enumerate(table_rows[1:], start=1):
            item = {
                'index': index,
                'case_id': '',
                'scenario': '',
                'precondition': '',
                'steps': '',
                'expected': '',
                'priority': 'P2'
            }
            for col_index, header in enumerate(headers):
                value = row[col_index] if col_index < len(row) else ''
                value = re.sub(r'<br\s*/?>', '\n', value, flags=re.IGNORECASE)
                if '用例' in header or header == 'id':
                    item['case_id'] = value
                elif '场景' in header or '目标' in header or '标题' in header:
                    item['scenario'] = value
                elif '前置' in header:
                    item['precondition'] = value
                elif '步骤' in header and '预期' not in header:
                    item['steps'] = value
                elif '预期' in header or '结果' in header:
                    item['expected'] = value
                elif '优先级' in header or header == 'priority':
                    item['priority'] = value or 'P2'
            if item['scenario'] or item['case_id']:
                results.append(item)
        return results

    results = []
    current_case = None
    for line in lines:
        if line.startswith(('1.', '2.', '3.', '4.', '5.')) or '测试用例' in line or 'Test Case' in line:
            if current_case:
                results.append(current_case)
            current_case = {
                'index': len(results) + 1,
                'case_id': f"TC{len(results) + 1:03d}",
                'scenario': re.sub(r'^(\d+\.|测试用例[:：]?\s*|Test Case[:：]?\s*)', '', line).strip(),
                'precondition': '',
                'steps': '',
                'expected': '',
                'priority': 'P2'
            }
        elif current_case and ('前置条件' in line or '前提' in line):
            current_case['precondition'] = re.sub(r'.*?[:：]\s*', '', line).strip()
        elif current_case and ('测试步骤' in line or '操作步骤' in line or '步骤' in line):
            current_case['steps'] = re.sub(r'.*?[:：]\s*', '', line).strip()
        elif current_case and ('预期结果' in line or 'Expected' in line):
            current_case['expected'] = re.sub(r'.*?[:：]\s*', '', line).strip()
        elif current_case and '优先级' in line:
            current_case['priority'] = re.sub(r'.*?[:：]\s*', '', line).strip() or 'P2'

    if current_case:
        results.append(current_case)

    return results


class RequirementDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = RequirementDocument
        fields = ['id', 'title', 'file', 'file_url', 'document_type', 'document_type_display', 
                 'status', 'status_display', 'uploaded_by', 'uploaded_by_name', 'project', 
                 'project_name', 'created_at', 'updated_at', 'file_size', 'extracted_text']
        read_only_fields = ['uploaded_by', 'file_size', 'extracted_text']
    
    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None


class BusinessRequirementSerializer(serializers.ModelSerializer):
    requirement_type_display = serializers.CharField(source='get_requirement_type_display', read_only=True)
    requirement_level_display = serializers.CharField(source='get_requirement_level_display', read_only=True)
    parent_requirement_name = serializers.CharField(source='parent_requirement.requirement_name', read_only=True)
    
    class Meta:
        model = BusinessRequirement
        fields = ['id', 'requirement_id', 'requirement_name', 'requirement_type', 
                 'requirement_type_display', 'parent_requirement', 'parent_requirement_name',
                 'module', 'requirement_level', 'requirement_level_display', 'reviewer', 
                 'estimated_hours', 'description', 'acceptance_criteria', 'created_at', 'updated_at']


class RequirementAnalysisSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document.title', read_only=True)
    document_id = serializers.IntegerField(source='document.id', read_only=True)
    project_id = serializers.IntegerField(source='document.project.id', read_only=True)
    project_name = serializers.CharField(source='document.project.name', read_only=True)
    requirements = BusinessRequirementSerializer(many=True, read_only=True)
    input_content_summary = serializers.SerializerMethodField()
    analysis_status = serializers.CharField(source='document.status', read_only=True)
    last_analysis_at = serializers.DateTimeField(source='updated_at', read_only=True)
    
    class Meta:
        model = RequirementAnalysis
        fields = ['id', 'document_id', 'document_title', 'analysis_report', 
                 'requirements_count', 'analysis_time', 'created_at', 'updated_at', 'requirements',
                 'project_id', 'project_name', 'input_content_summary', 'analysis_status', 'last_analysis_at']

    def get_input_content_summary(self, obj):
        document = obj.document
        return {
            'title': document.title,
            'document_type': document.document_type,
            'document_type_display': document.get_document_type_display(),
            'file_size': document.file_size,
            'text_length': len(document.extracted_text or ''),
            'label': f"{document.get_document_type_display()} / {document.title}"
        }


class GeneratedTestCaseSerializer(serializers.ModelSerializer):
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    requirement_name = serializers.CharField(source='requirement.requirement_name', read_only=True)
    requirement_id_display = serializers.CharField(source='requirement.requirement_id', read_only=True)
    project_id = serializers.IntegerField(source='requirement.analysis.document.project.id', read_only=True)
    project_name = serializers.CharField(source='requirement.analysis.document.project.name', read_only=True)
    source_task_id = serializers.SerializerMethodField()
    save_status_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = GeneratedTestCase
        fields = ['id', 'case_id', 'title', 'priority', 'priority_display', 'precondition',
                 'test_steps', 'expected_result', 'status', 'status_display', 'generated_by_ai',
                 'reviewed_by_ai', 'review_comments', 'requirement', 'requirement_name', 
                 'requirement_id_display', 'project_id', 'project_name',
                 'source_task_id', 'save_status_summary', 'created_at', 'updated_at']

    def get_source_task_id(self, obj):
        return ''

    def get_save_status_summary(self, obj):
        return {
            'is_saved_to_testcases': obj.status == 'adopted',
            'label': '已保存为测试用例' if obj.status == 'adopted' else '尚未保存为正式测试用例'
        }


class AnalysisTaskSerializer(serializers.ModelSerializer):
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalysisTask
        fields = ['id', 'task_id', 'task_type', 'task_type_display', 'document', 'document_title',
                 'status', 'status_display', 'progress', 'result', 'error_message', 
                 'started_at', 'completed_at', 'created_at', 'duration']
        read_only_fields = ['task_id', 'result', 'error_message', 'started_at', 'completed_at']
    
    def get_duration(self, obj):
        if obj.started_at and obj.completed_at:
            return (obj.completed_at - obj.started_at).total_seconds()
        return None


class DocumentUploadSerializer(serializers.ModelSerializer):
    """文档上传专用序列化器"""
    class Meta:
        model = RequirementDocument
        fields = ['id', 'title', 'file', 'project']
    
    def create(self, validated_data):
        # 自动设置上传者（如果用户已登录）
        user = self.context['request'].user
        if user.is_authenticated:
            validated_data['uploaded_by'] = user
        else:
            # 如果是匿名用户，使用第一个超级用户作为默认用户
            from apps.users.models import User
            default_user = User.objects.filter(is_superuser=True).first()
            if not default_user:
                default_user = User.objects.first()
            validated_data['uploaded_by'] = default_user
        
        # 根据文件扩展名设置文档类型
        file = validated_data['file']
        if file.name.lower().endswith('.pdf'):
            validated_data['document_type'] = 'pdf'
        elif file.name.lower().endswith(('.doc', '.docx')):
            validated_data['document_type'] = 'docx'
        elif file.name.lower().endswith('.txt'):
            validated_data['document_type'] = 'txt'
        elif file.name.lower().endswith('.md'):
            validated_data['document_type'] = 'md'
        
        # 设置文件大小
        validated_data['file_size'] = file.size
        
        return super().create(validated_data)


class TestCaseGenerationRequestSerializer(serializers.Serializer):
    """测试用例生成请求序列化器"""
    requirement_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="需求ID列表"
    )
    test_level = serializers.ChoiceField(
        choices=[('unit', '单元测试'), ('integration', '集成测试'), ('system', '系统测试'), ('acceptance', '验收测试')],
        default='system',
        help_text="测试级别"
    )
    test_priority = serializers.ChoiceField(
        choices=[('P0', '最高优先级'), ('P1', '高优先级'), ('P2', '中优先级'), ('P3', '低优先级')],
        default='P1',
        help_text="测试优先级"
    )
    test_case_count = serializers.IntegerField(
        min_value=1,
        max_value=200,
        default=50,
        help_text="生成测试用例数量"
    )


class TestCaseReviewRequestSerializer(serializers.Serializer):
    """测试用例评审请求序列化器"""
    test_case_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="测试用例ID列表"
    )
    review_criteria = serializers.CharField(
        max_length=500,
        default="检查测试用例的完整性、准确性和可执行性",
        help_text="评审标准"
    )


class AIModelConfigSerializer(serializers.ModelSerializer):
    """AI模型配置序列化器"""
    model_type_display = serializers.CharField(source='get_model_type_display', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    api_key_masked = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = AIModelConfig
        fields = ['id', 'name', 'model_type', 'model_type_display', 'role', 'role_display',
                 'api_key', 'api_key_masked', 'base_url', 'model_name', 'max_tokens', 'temperature', 'top_p', 
                 'is_active', 'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_by_name']
        extra_kwargs = {
            'api_key': {'write_only': True}  # API Key只用于写入，不在响应中返回
        }
    
    def get_api_key_masked(self, obj):
        """返回掩码版本的API Key"""
        if obj.api_key:
            # 显示前3个字符和后4个字符，中间用*替代
            if len(obj.api_key) > 7:
                return f"{obj.api_key[:3]}{'*' * (len(obj.api_key) - 7)}{obj.api_key[-4:]}"
            else:
                return '*' * len(obj.api_key)
        return ''
    
    def create(self, validated_data):
        # 自动设置创建者
        user = self.context['request'].user
        if user.is_authenticated:
            validated_data['created_by'] = user
        else:
            # 如果是匿名用户，使用第一个超级用户作为默认用户
            from apps.users.models import User
            default_user = User.objects.filter(is_superuser=True).first()
            if not default_user:
                default_user = User.objects.first()
            validated_data['created_by'] = default_user
        
        return super().create(validated_data)


class PromptConfigSerializer(serializers.ModelSerializer):
    """提示词配置序列化器"""
    prompt_type_display = serializers.CharField(source='get_prompt_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = PromptConfig
        fields = ['id', 'name', 'prompt_type', 'prompt_type_display', 'content', 'is_active',
                 'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_by_name']
    
    def create(self, validated_data):
        # 自动设置创建者
        user = self.context['request'].user
        if user.is_authenticated:
            validated_data['created_by'] = user
        else:
            # 如果是匿名用户，使用第一个超级用户作为默认用户
            from apps.users.models import User
            default_user = User.objects.filter(is_superuser=True).first()
            if not default_user:
                default_user = User.objects.first()
            validated_data['created_by'] = default_user
        
        return super().create(validated_data)


class TestCaseGenerationTaskSerializer(serializers.ModelSerializer):
    """测试用例生成任务序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    writer_model_name = serializers.CharField(source='writer_model_config.name', read_only=True)
    reviewer_model_name = serializers.CharField(source='reviewer_model_config.name', read_only=True)
    writer_prompt_name = serializers.CharField(source='writer_prompt_config.name', read_only=True)
    reviewer_prompt_name = serializers.CharField(source='reviewer_prompt_config.name', read_only=True)
    generation_config_summary = serializers.SerializerMethodField()
    result_count = serializers.SerializerMethodField()
    save_status_summary = serializers.SerializerMethodField()
    generated_results_preview = serializers.SerializerMethodField()
    source_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = TestCaseGenerationTask
        fields = ['id', 'task_id', 'title', 'requirement_text', 'status', 'status_display',
                 'progress', 'project', 'project_name', 'writer_model_config', 'writer_model_name', 
                 'reviewer_model_config', 'reviewer_model_name', 'writer_prompt_config', 'writer_prompt_name',
                 'reviewer_prompt_config', 'reviewer_prompt_name', 'generated_test_cases',
                 'review_feedback', 'final_test_cases', 'generation_log', 'error_message',
                 'created_by', 'created_by_name', 'created_at', 'updated_at', 'completed_at',
                 'generation_config_summary', 'result_count', 'save_status_summary',
                 'generated_results_preview', 'source_summary', 'is_saved_to_records', 'saved_at']
        read_only_fields = ['task_id', 'status', 'progress', 'generated_test_cases', 
                          'review_feedback', 'final_test_cases', 'generation_log', 
                          'error_message', 'created_by', 'completed_at']

    def get_generation_config_summary(self, obj):
        config = GenerationConfig.get_active_config()
        return {
            'name': config.name if config else '',
            'is_inferred': True,
            'label': f"当前活跃配置：{config.name}" if config else '未找到活跃生成配置',
            'detail': '当前任务模型未持久化任务级生成配置，本轮先展示当前活跃配置摘要。'
        }

    def get_result_count(self, obj):
        return len(_parse_generated_results(obj.final_test_cases or obj.generated_test_cases))

    def get_save_status_summary(self, obj):
        return {
            'is_saved': obj.is_saved_to_records,
            'label': '已保存为正式测试用例' if obj.is_saved_to_records else '尚未保存为正式测试用例',
            'saved_at': obj.saved_at
        }

    def get_generated_results_preview(self, obj):
        return _parse_generated_results(obj.final_test_cases or obj.generated_test_cases)[:3]

    def get_source_summary(self, obj):
        return {
            'project_id': obj.project_id,
            'project_name': obj.project.name if obj.project else '',
            'label': f"来源项目：{obj.project.name}" if obj.project else '来源项目未记录',
            'detail': '生成任务对象承接测试设计项目、需求输入与 AI 配置上下文。'
        }
    
    def create(self, validated_data):
        # 自动设置创建者和任务ID
        import uuid
        user = self.context['request'].user
        if user.is_authenticated:
            validated_data['created_by'] = user
        else:
            from apps.users.models import User
            default_user = User.objects.filter(is_superuser=True).first()
            if not default_user:
                default_user = User.objects.first()
            validated_data['created_by'] = default_user
        
        validated_data['task_id'] = f"TASK_{uuid.uuid4().hex[:8].upper()}"
        
        return super().create(validated_data)


class TestCaseGenerationRequestSerializer(serializers.Serializer):
    """新的测试用例生成请求序列化器"""
    title = serializers.CharField(max_length=200, help_text="任务标题")
    requirement_text = serializers.CharField(help_text="需求描述")
    project = serializers.IntegerField(required=False, allow_null=True, help_text="关联项目ID")
    use_writer_model = serializers.BooleanField(default=True, help_text="是否使用编写模型")
    use_reviewer_model = serializers.BooleanField(default=True, help_text="是否使用评审模型")


class GenerationConfigSerializer(serializers.ModelSerializer):
    """生成行为配置序列化器"""
    default_output_mode_display = serializers.CharField(source='get_default_output_mode_display', read_only=True)

    class Meta:
        model = GenerationConfig
        fields = [
            'id', 'name', 'default_output_mode', 'default_output_mode_display',
            'enable_auto_review', 'review_timeout',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

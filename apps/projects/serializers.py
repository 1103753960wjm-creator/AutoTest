from rest_framework import serializers
from .models import Project, ProjectMember, ProjectEnvironment
from apps.users.serializers import UserSerializer

class ProjectSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name')

class ProjectEnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectEnvironment
        fields = '__all__'

class ProjectMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ProjectMember
        fields = ['id', 'user', 'user_id', 'role', 'joined_at']

class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = ProjectMemberSerializer(source='projectmember_set', many=True, read_only=True)
    environments = ProjectEnvironmentSerializer(many=True, read_only=True)
    testcase_count = serializers.SerializerMethodField()
    requirement_summary = serializers.SerializerMethodField()
    ai_generation_summary = serializers.SerializerMethodField()
    automation_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'status', 'owner', 'members', 
                 'environments', 'created_at', 'updated_at', 'testcase_count',
                 'requirement_summary', 'ai_generation_summary', 'automation_summary']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_testcase_count(self, obj):
        return obj.testcases.count()

    def get_requirement_summary(self, obj):
        documents = obj.requirement_documents.all()
        document_count = documents.count()
        analyzed_count = documents.filter(status='analyzed').count()
        latest_document = documents.order_by('-updated_at').first()
        latest_analysis = None
        if latest_document and hasattr(latest_document, 'analysis'):
            latest_analysis = latest_document.analysis

        return {
            'document_count': document_count,
            'analyzed_count': analyzed_count,
            'latest_document_title': latest_document.title if latest_document else '',
            'latest_analysis_at': latest_analysis.updated_at if latest_analysis else None,
            'label': f'已上传 {document_count} 份需求输入，完成分析 {analyzed_count} 份'
            if document_count
            else '尚未关联需求输入'
        }

    def get_ai_generation_summary(self, obj):
        tasks = obj.generation_tasks.all().order_by('-created_at')
        task_count = tasks.count()
        completed_count = tasks.filter(status='completed').count()
        saved_count = tasks.filter(is_saved_to_records=True).count()
        latest_task = tasks.first()

        return {
            'task_count': task_count,
            'completed_count': completed_count,
            'saved_count': saved_count,
            'latest_task_id': latest_task.task_id if latest_task else '',
            'latest_status': latest_task.status if latest_task else '',
            'latest_updated_at': latest_task.updated_at if latest_task else None,
            'label': f'共 {task_count} 个生成任务，完成 {completed_count} 个，已保存 {saved_count} 个'
            if task_count
            else '尚未发起 AI 生成任务'
        }

    def get_automation_summary(self, obj):
        return {
            'status': 'pending',
            'label': '自动化草稿中心待接入',
            'detail': '本轮仅预留项目级自动化状态位，2.3 再挂接自动化草稿中心。'
        }

class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['name', 'description', 'status']
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

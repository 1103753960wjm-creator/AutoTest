from rest_framework import generics, permissions, status, pagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db import models
from .models import TestCase, TestCaseStep, TestCaseAttachment, TestCaseComment
from .serializers import (
    TestCaseSerializer, TestCaseListSerializer, TestCaseCreateSerializer, TestCaseUpdateSerializer
)
from .ai_source_dedup import extract_ai_generation_source, get_or_create_ai_testcase
from apps.requirement_analysis.models import TestCaseGenerationTask
from apps.requirement_analysis.result_status import mark_result_status
from apps.projects.models import Project
from apps.versions.models import Version

class TestCasePagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class TestCaseListCreateView(generics.ListCreateAPIView):
    queryset = TestCase.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TestCasePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['priority', 'test_type', 'project']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TestCaseCreateSerializer
        return TestCaseListSerializer
    
    def get_queryset(self):
        user = self.request.user
        accessible_projects = Project.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct()
        return TestCase.objects.filter(
            project__in=accessible_projects
        ).select_related(
            'author', 'assignee', 'project'
        ).prefetch_related(
            'versions'
        ).distinct()
    
    def get_user_accessible_projects(self, user):
        """获取用户有权限访问的项目"""
        return Project.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct()
    
    def get_default_version_ids_for_project(self, project):
        if not project:
            return []

        baseline_ids = list(
            Version.objects.filter(projects=project, is_baseline=True).values_list('id', flat=True)
        )
        if baseline_ids:
            return baseline_ids

        project_version_ids = list(
            Version.objects.filter(projects=project).order_by('-created_at').values_list('id', flat=True)
        )
        if len(project_version_ids) == 1:
            return project_version_ids

        return []

    def should_apply_ai_default_versions(self):
        version_ids = self.request.data.get('version_ids')
        if version_ids:
            return False

        tags = self.request.data.get('tags')
        if not isinstance(tags, list):
            return False

        return any(isinstance(tag, dict) and tag.get('source') == 'ai_generation_task' for tag in tags)

    def resolve_target_project(self, user, project_id):
        accessible_projects = self.get_user_accessible_projects(user)

        if project_id:
            try:
                return accessible_projects.get(id=project_id)
            except Project.DoesNotExist:
                project = accessible_projects.first()
                if project:
                    return project
        else:
            project = accessible_projects.first()
            if project:
                return project

        return Project.objects.create(
            name="默认项目",
            owner=user,
            description='系统自动创建的默认项目'
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        project = self.resolve_target_project(user, request.data.get('project_id'))
        validated_payload = dict(serializer.validated_data)
        ai_source = extract_ai_generation_source(validated_payload.get('tags'))

        if ai_source:
            testcase, created, normalized_payload, _ = get_or_create_ai_testcase(
                project=project,
                testcase_payload=validated_payload,
                create_callback=lambda payload: serializer.save(author=user, project=project, tags=payload.get('tags', [])),
                apply_default_versions=self._apply_default_versions_if_needed,
            )
            self._sync_ai_task_result_status(ai_source, testcase)
            response_serializer = TestCaseSerializer(testcase, context=self.get_serializer_context())
            response_data = dict(response_serializer.data)
            response_data['deduplicated'] = not created
            response_data['existing_id'] = None if created else testcase.id
            if not created:
                response_data['message'] = '该 AI 生成结果已采纳，返回已有测试用例'
            headers = self.get_success_headers(serializer.data if created else {})
            return Response(
                response_data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
                headers=headers,
            )

        testcase = serializer.save(author=user, project=project)
        if self.should_apply_ai_default_versions():
            self._apply_default_versions_if_needed(testcase, project)

        response_serializer = TestCaseSerializer(testcase, context=self.get_serializer_context())
        headers = self.get_success_headers(serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def _sync_ai_task_result_status(self, ai_source, testcase):
        task_id = str(ai_source.get('task_id') or '').strip()
        if not task_id:
            return

        task = TestCaseGenerationTask.objects.filter(task_id=task_id).first()
        if not task:
            return

        mark_result_status(
            task,
            case_id=ai_source.get('case_id') or '',
            case_index=ai_source.get('case_index'),
            status='adopted',
            adopted_testcase_id=testcase.id,
            save=True,
        )

    def _apply_default_versions_if_needed(self, testcase, project):
        if not self.should_apply_ai_default_versions():
            return

        if testcase.versions.exists():
            return

        default_version_ids = self.get_default_version_ids_for_project(project)
        if default_version_ids:
            testcase.versions.set(default_version_ids)

    def perform_create(self, serializer):
        user = self.request.user
        project = self.resolve_target_project(user, self.request.data.get('project_id'))
        testcase = serializer.save(author=user, project=project)
        self._apply_default_versions_if_needed(testcase, project)

class TestCaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestCase.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TestCaseUpdateSerializer
        return TestCaseSerializer
    
    def get_queryset(self):
        user = self.request.user
        accessible_projects = Project.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct()
        return TestCase.objects.filter(
            project__in=accessible_projects
        ).select_related(
            'author', 'assignee', 'project'
        ).prefetch_related(
            'versions', 'step_details', 'attachments', 'comments'
        )
    
    def get_user_accessible_projects(self, user):
        """获取用户有权限访问的项目"""
        return Project.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct()
    
    def perform_update(self, serializer):
        user = self.request.user
        project_id = self.request.data.get('project_id')
        
        if project_id:
            # 检查指定的项目是否存在且用户有权限
            accessible_projects = self.get_user_accessible_projects(user)
            try:
                project = accessible_projects.get(id=project_id)
                serializer.save(project=project)
            except Project.DoesNotExist:
                # 如果指定项目不存在或无权限，保持原项目不变
                serializer.save()
        else:
            # 没有指定项目，保持原项目不变
            serializer.save()

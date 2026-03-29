from django.urls import path
from . import views

urlpatterns = [
    path('', views.VersionListCreateView.as_view(), name='version-list'),
    path('batch-delete/', views.version_batch_delete, name='version-batch-delete'),
    path('<int:pk>/', views.VersionDetailView.as_view(), name='version-detail'),
    path('projects/<int:project_id>/versions/', views.get_project_versions, name='project-versions'),
]

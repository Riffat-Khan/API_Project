from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.ProfileRegister.as_view({
        'post': 'create',
    }), name='register'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('projects/', views.ProjectRegister.as_view({
        'post': 'create',
        'get': 'list'
    }), name='projects'),
    path('projects/<int:pk>/', views.ProjectRegister.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }), name='projects_id'),
     path('tasks/', views.TaskRegister.as_view({
        'post': 'create',
        'get': 'list'
    }), name='task'),
    path('tasks/<int:pk>/', views.TaskRegister.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }), name='task_id'),
     path('documents/', views.DocumentRegister.as_view({
        'post': 'create',
        'get': 'list'
    }), name='document'),
    path('documents/<int:pk>/', views.DocumentRegister.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }), name='document_id'),
     path('comments/', views.Comments.as_view({
        'post': 'create',
        'get': 'list'
    }), name='comment'),
    path('comments/<int:pk>/', views.Comments.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }), name='comment_id'),
]


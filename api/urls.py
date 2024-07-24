from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.ProfileRegister.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('projects/', views.ProjectRegister.as_view(), name='projects'),
    path('projects/<int:id>/', views.GetPutDelProjectAPI.as_view(), name='projects_id'),
    path('tasks/', views.TaskRegister.as_view(), name='tasks'),
    path('tasks/<int:id>/', views.GetPutDelTaskAPI.as_view(), name='tasks_id'),
    # path('tasks/<int:task_id>/assign/', views.GetPutDelTaskAPI.as_view(), name='tasks_assign'),
    path('documents/', views.DocumentRegister.as_view(), name='doc'),
    path('documents/<int:id>/', views.GetPutDelDocumentAPI.as_view(), name='doc'),
    path('comments/', views.CommentRegister.as_view(), name='comments'),
    path('comments/<int:id>/', views.GetPutDelCommentAPI.as_view(), name='comments'),
] 
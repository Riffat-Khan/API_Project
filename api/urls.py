from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()

router.register(r'register', views.ProfileRegister, basename='profile')
router.register(r'projects', views.ProjectRegister, basename='projects')
router.register(r'tasks', views.TaskRegister, basename='tasks')
router.register(r'documents', views.DocumentRegister, basename='documents')
router.register(r'comments', views.CommentsRegister, basename='comments')
router.register(r'timeline', views.TimelineDisplay, basename='timeline')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
]


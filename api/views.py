from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from . import serializers
from .enum import RoleChoice
from .permissions import IsManager
from .models import Profile, Project, Task, Document, Comment, Timeline, Notification


class ProfileRegister(viewsets.ModelViewSet):
    serializer_class = serializers.UserRegisterSerializer


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({'message': 'Logout successful'}, status=status.HTTP_205_RESET_CONTENT)
            except Exception:
                return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'No refresh token provided'}, status=status.HTTP_400_BAD_REQUEST)


class ProjectRegister(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ProjectRegisterSerializer
    
    def get_queryset(self):
        
        user_profile = Profile.objects.get(user=self.request.user)
        users_id = user_profile.id
        print(f"User Profile: {user_profile}")
        if user_profile.role == RoleChoice.MANAGER.value:
            return Project.objects.all()
        else:
            return Project.objects.filter(team_members=users_id)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, *args, **kwargs):
        user_profile = Profile.objects.get(user=request.user)
        if user_profile.role != RoleChoice.MANAGER.value:
            return Response({"message": "Only managers can delete project."}, status=status.HTTP_404_NOT_FOUND)
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

class TaskRegister(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.TaskRegisterSerializer 
    
    def get_queryset(self):
        user_profile = Profile.objects.get(user=self.request.user)
        if user_profile.role == RoleChoice.MANAGER.value:
            return Task.objects.all()
        return Task.objects.filter(assignee=user_profile)
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def destroy(self, request, *args, **kwargs):
        user_profile = Profile.objects.get(user=request.user)
        if user_profile.role != RoleChoice.MANAGER.value:
            return Response({"message": "Only managers can delete task."}, status=status.HTTP_404_NOT_FOUND)
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)     
    

class DocumentRegister(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.DocumentRegisterSerializer
    
    def get_queryset(self):
        user_profile = Profile.objects.get(user=self.request.user)
        if user_profile.role == RoleChoice.MANAGER.value:
            return Document.objects.all()
        else:
            assigned_tasks = Task.objects.filter(assignee=user_profile)
            project_ids = assigned_tasks.values_list('project_id', flat=True)
            return Document.objects.filter(project_id__in=project_ids)
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.request.user.profile
        user_profile = Profile.objects.get(user=self.request.user)
        project = instance.project
        if (user_profile in project.team_members.all()) or (user_profile.role != RoleChoice.MANAGER.value):
            return Response({"message": "Only managers can delete projects."}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT) 


class CommentsRegister(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CommentRegisterSerializer
    
    def get_queryset(self):
        user_profile = Profile.objects.get(user=self.request.user)
        if user_profile.role == RoleChoice.MANAGER.value:
            return Comment.objects.all()
        else:
            return Comment.objects.filter(author=self.request.user)
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user_profile = Profile.objects.get(user=self.request.user)
        if instance.author != request.user:
            return Response({"message": "You do not have permission to delete this comment."}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
    
class TimelineDisplay(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = serializers.TimelineSerializer
    queryset = Timeline.objects.all()
    

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = serializers.NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user)
    
    @action(detail=True, methods=['put'])
    def mark_read(self, request, pk=None):
        try:
            notification = self.get_object()
            if notification.user != request.user:
                return Response({'detail': 'You do not have permission to modify this notification.'}, status=status.HTTP_403_FORBIDDEN)
            serializer = self.get_serializer(notification, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Notification.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        
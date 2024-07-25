from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from . import serializers
from .permissions import IsManager
from .models import Profile, Project, Task, Document, Comment


class ProfileRegister(viewsets.ModelViewSet):
    serializer_class = serializers.UserRegisterSerializer
    Model = Profile
    queryset = Profile.objects.all()
    
        
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        else:
            return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)


class ProjectRegister(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    Model = Project
    queryset = Project.objects.all()
    serializer_class = serializers.ProjectRegisterSerializer
    
    def get_queryset(self):
        user_profile = Profile.objects.get(user=self.request.user)
        if user_profile.role == 'manager':
            return Project.objects.all()
        else:
            return Project.objects.filter(team_members__in=[user_profile])
    
    def list(self, request, *args, **kwargs):
        user_profile = Profile.objects.get(user=self.request.user)
        if user_profile.role != 'manager':
            raise PermissionDenied("You do not have permission to view this list.")
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, *args, **kwargs):
        user_profile = Profile.objects.get(user=request.user)
        if user_profile.role != 'MANAGER':
            raise PermissionDenied("Only managers can delete projects.")
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

class TaskRegister(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsManager]
    Model = Task
    queryset = Task.objects.all()
    field_value = 1
    serializer_class = serializers.TaskRegisterSerializer 
    
    def get_queryset(self):
        user_profile = Profile.objects.get(user=self.request.user)
        if user_profile.role == 'manager':
            return Task.objects.all()
        else:
            return Task.objects.filter(assignee__in=[user_profile])
        
    def list(self, request, *args, **kwargs):
        user_profile = Profile.objects.get(user=self.request.user)
        if user_profile.role != 'manager':
            raise PermissionDenied("You do not have permission to view this list.")
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def destroy(self, request, *args, **kwargs):
        user_profile = Profile.objects.get(user=request.user)
        if user_profile.role != 'MANAGER':
            raise PermissionDenied("Only managers can delete projects.")
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)     
    

class DocumentRegister(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    Model = Document
    queryset = Document.objects.all()
    serializer_class = serializers.DocumentRegisterSerializer
    
    def get_queryset(self):
        user_profile = Profile.objects.get(user=self.request.user)
        if user_profile.role == 'manager':
            return Document.objects.all()
        else:
            assigned_tasks = Task.objects.filter(assignee=user_profile)
            project_ids = assigned_tasks.values_list('project_id', flat=True)
            return Document.objects.filter(project_id__in=project_ids)
        
    def list(self, request, *args, **kwargs):
        user_profile = Profile.objects.get(user=self.request.user)
        if user_profile.role != 'manager':
            raise PermissionDenied("You do not have permission to view this list.")
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user_profile = Profile.objects.get(user=self.request.user)
        project = instance.project
        if (user_profile in project.team_members.all()) and (user_profile.role != 'MANAGER'):
            raise PermissionDenied("Only managers can delete projects.")
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT) 


class Comments(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentRegisterSerializer
    Model = Comment
    
    def get_queryset(self):
        user_profile = Profile.objects.get(user=self.request.user)
        if user_profile.role == 'manager':
            return Comment.objects.all()
        else:
            return Comment.objects.filter(task__assignee = user_profile)
        
    def list(self, request, *args, **kwargs):
        user_profile = Profile.objects.get(user=self.request.user)
        if user_profile.role != 'manager':
            raise PermissionDenied("You do not have permission to view this list.")
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user_profile = Profile.objects.get(user=self.request.user)
        if instance.author != request.user and user_profile.role != 'manager':
            raise PermissionDenied("You do not have permission to delete this comment.")
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
    
    
    

        
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from . import serializers
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Profile, Project, Task, Document, Comment
from .permissions import IsManager


class RegisterAPI(APIView):  
    serializer_class = None
    Model = None
    field_value = None

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

    def get(self,request):
        if self.Model in [Task, Document, Comment]:
            queryset = self.Model.objects.filter(project=self.field_value)
        else:
            queryset = self.Model.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetPutDelAPI(APIView):
    serializer_class = None
    Model = None

    def get(self, request, id):
        try:
            queryset = self.Model.objects.get(id=id)
        except self.Model.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, id):
        try:
            queryset = self.Model.objects.get(id=id)
        except self.Model.DoesNotExist:
            return Response({"message": "Task not found!"}, status=status.HTTP_440_NOT_FOUND)
        
        serializer = self.serializer_class(queryset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        try:
            queryset = self.Model.objects.get(id=id)
            queryset.delete()
            return Response({"message": "Task deleted"}, status=status.HTTP_200_OK)
        except self.Model.DoesNotExist:
            return Response({"message": "Task not found!"}, status=status.HTTP_440_NOT_FOUND)


class ProfileRegister(RegisterAPI):
    serializer_class = serializers.UserRegisterSerializer
    Model = Profile
    field_value = 'None'


class UserLoginView(APIView):
    def post(self, request):
        serializer = serializers.UserLoginSerializer(data=request.data)
        if serializer.is_valid(): 
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                user_data = serializers.UserRegisterSerializer(user)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'data': user_data.data
                    }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
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


class ProjectRegister(RegisterAPI):
    permission_classes = [IsAuthenticated, IsManager]
    Model = Project
    field_value = 1
    serializer_class = serializers.ProjectRegisterSerializer
    

class GetPutDelProjectAPI(GetPutDelAPI):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = serializers.ProjectRegisterSerializer
    Model = Project
 

class TaskRegister(RegisterAPI):
    permission_classes = [IsAuthenticated, IsManager]
    Model = Task
    field_value = 1
    serializer_class = serializers.TaskRegisterSerializer
          

class GetPutDelTaskAPI(GetPutDelAPI):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = serializers.TaskRegisterSerializer
    Model = Task
    
        
class TaskAssignAPI(APIView):
    permission_classes = [IsAuthenticated, IsManager]
    
    def post(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"message": "Task not found"}, status=status.HTTP_440_NOT_FOUND)
        
        assign_id = Task.objects.get('assignee')
        
        assign = Profile.objects.get(id=assign_id)
        task.assignee = assign
        task.save()
        
        serializer = serializers.TaskRegisterSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DocumentRegister(RegisterAPI):
    permission_classes = [IsAuthenticated]
    Model = Document
    field_value = 1
    serializer_class = serializers.DocumentRegisterSerializer


class GetPutDelDocumentAPI(GetPutDelAPI):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.DocumentRegisterSerializer
    Model = Document
    

class CommentRegister(RegisterAPI):
    permission_classes = [IsManager]
    serializer_class = serializers.CommentRegisterSerializer
    Model = Comment
    
    
    
class GetPutDelCommentAPI(GetPutDelAPI):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CommentRegisterSerializer
    Model = Comment
    
from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.models import User
from .enum import StatusChoice, RoleChoice
from .models import Profile, Project, Task, Document, Comment

class ProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profile
        fields = ['profile_picture', 'role', 'contact_number']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'profile']
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
        }
        
    def validate(self, data):
        username = data.get('username')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already exists.")
        
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        
        profile_data = data.get('profile', {})
        role = profile_data.get('role')
        if not role or role not in RoleChoice._value2member_map_:
            raise serializers.ValidationError("Valid Role choice is required in the profile.")
        if not profile_data.get('contact_number'):
            raise serializers.ValidationError("Contact number is required in the profile.")
        
        return data
        
    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'] 
        )
        Profile.objects.create(user=user, **profile_data)
        return user


class ProjectRegisterSerializer(serializers.ModelSerializer):
    team_members = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(),
        many=True
    )

    class Meta:
        model = Project
        fields = ['title', 'description', 'start_date', 'end_date', 'team_members']
        
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        user = self.context['request'].user
        
        if user.profile.role != 'manager':
            raise serializers.ValidationError("Only manager has access to it")
    
        title = data.get('title')
        if title :
            if Project.objects.filter(title=title).exists():
                raise serializers.ValidationError("A task with this title already exists in the specified project.")
        
        if start_date and end_date and start_date < timezone.now().date() and end_date < start_date:
            raise serializers.ValidationError("Start date must be equal to or greater than the current date and End date must be greater than Start date")
        
        return data
        
class TaskRegisterSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all()
    )
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(),
    )
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'project', 'assignee']
        
    def validate(self, data):
        user = self.context['request'].user
        
        project = data.get('project')
        
        title = data.get('title')
        if title and project:
            if Task.objects.filter(title=title, project=project).exists():
                raise serializers.ValidationError("A task with this title already exists in the specified project.")
            
        assignee = data.get('assignee')   
        if assignee:
            if not project.team_members.filter(id=assignee.id).exists():
                raise serializers.ValidationError("The assignee is not a member of the project.")
            
        if project not in Project.objects.all():
            raise serializers.ValidationError("The project doesent exist")
        
        status = data.get('status')
        if status not in StatusChoice._value2member_map_:
            raise serializers.ValidationError("Invalid status choice")
        
        return data
    
    
class DocumentRegisterSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all()
    )
    
    class Meta:
        model = Document
        fields = ['name', 'description', 'file', 'version', 'project']
        
    def validate(self, data):
        user = self.context['request'].user

        project = data.get('project')
        if not user.profile.role == 'manager':
            if project and not project.team_members.filter(id=user.id).exists():
                raise serializers.ValidationError("You are not a member of this project and cannot add documents.")
        
        name = data.get('name')
        if name and project:
            if Document.objects.filter(name=name, project=project).exists():
                raise serializers.ValidationError("A document with this name already exists in the specified project.")

        return data
        
        
class CommentRegisterSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all()
    )
    task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all()
    )
    
    class Meta:
        model = Comment
        fields = ['text', 'author', "created_at", 'project', 'task']
    
    def validate(self, data):
        user = self.context['request'].user
    
        if 'author' in data and data['author'] != user:
            raise serializers.ValidationError("You cannot set a different author for the comment.")
        
        task = data.get('task')
        project = data.get('project')
        
        if not user.profile.role == 'manager':
            if project and not project.members.filter(id=user.id).exists():
                raise serializers.ValidationError("You are not a member of this project.")
        
        if task and task.project != project:
            raise serializers.ValidationError("The task does not belong to the specified project.")
        
        return data
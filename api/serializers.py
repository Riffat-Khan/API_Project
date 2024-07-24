from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Profile, Project, Task, Document, Comment

class ProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profile
        fields = ['profile_picture', 'role', 'contact_number']


class UserRegisterSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['username', 'password', 'profile']
        
    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, **profile_data)
        return user

    
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data.get('username'), password=data.get('password'))
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        return data
    

class ProjectRegisterSerializer(serializers.ModelSerializer):
    team_members = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(),
        many=True
    )

    class Meta:
        model = Project
        fields = ['title', 'description', 'start_date', 'end_date', 'team_members']
        
        
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
    
    
class DocumentRegisterSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all()
    )
    
    class Meta:
        model = Document
        fields = ['name', 'description', 'file', 'version', 'project']
        
        
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
        
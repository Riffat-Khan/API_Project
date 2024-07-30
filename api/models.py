from django.db import models
from django.contrib.auth.models import User
from .enum import RoleChoice, StatusChoice

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    role = models.CharField(max_length=100, choices=[(role.value, role.name) for role in RoleChoice])
    contact_number = models.CharField(max_length=15)
    
    def __str__(self) -> str:
        return super().__str__()


class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True)
    team_members = models.ManyToManyField(Profile)
    
    def __str__(self) -> str:
        return super().__str__()
    
    
class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=100, choices=[(role.value, role.name) for role in StatusChoice])
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assignee = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    
    def __str__(self) -> str:
        return super().__str__()
    
    
class Document(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    file = models.FileField(upload_to='documents/', null=True, blank=True)
    version = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return super().__str__()
    
    
class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return super().__str__()


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True, blank=True) 
    
    def __str__(self) -> str:
        return super().__str__()
    
    
class Timeline(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return super().__str__()
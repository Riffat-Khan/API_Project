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


class members(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    phone = models.IntegerField(null=True)
    date_join = models.DateField(null=True)
    salary = models.IntegerField(null=True)
    bonus = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    def __str__(self) -> str:
        return super().__str__()
    
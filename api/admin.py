from django.contrib import admin
from .models import Profile, Project, Task, Document, Comment, Timeline, Notification

admin.site.register(Profile)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Document)
admin.site.register(Comment)
admin.site.register(Timeline)
admin.site.register(Notification)
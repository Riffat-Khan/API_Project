from django.contrib import admin
from .models import Profile, Project, Task, Document, Comment

class id_display(admin.ModelAdmin):
    list_display = ('id' , 'role')

admin.site.register(Profile, id_display)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Document)
admin.site.register(Comment)
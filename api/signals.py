from django.db.models.signals import post_save, m2m_changed
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Project, Timeline, Notification

@receiver(post_save, sender=Project)
def create_timeline_on_project_save(sender, instance, created, **kwargs):
    if created:
        Timeline.objects.create(project=instance)
        
@receiver(m2m_changed, sender=Project.team_members.through)
def notify_members(sender, instance, action, **kwargs):
    if action == 'post_add':
        for user in kwargs.get('pk_set', []):
            user_instance = User.objects.get(pk=user)
            message = f"You have been added to the project: {instance.title}"
            Notification.objects.create(user=user_instance, project=instance, message=message)
            
            
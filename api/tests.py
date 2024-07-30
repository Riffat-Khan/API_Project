from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .enum import RoleChoice, StatusChoice
from .models import Profile, Project, Task, Document, Comment, Timeline, Notification

User = get_user_model()

class ProfileMethodTests(APITestCase):
    def setUp(self):
        pass

    def test_user_registration(self):
        data = {
            "username": "milli",
            "password": "Riffat@1100",
            "confirm_password": "Riffat@1100",
            "profile": {
                "role": RoleChoice.QA.value,
                "contact_number": "3439887746764"
            }
        }
        response = self.client.post('/api/register/', data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ProjectMethodsTests(APITestCase):

    def setUp(self):
        self.manager_user = User.objects.create_user(username='anas', password='Riffat@1100')
        self.manager_profile = Profile.objects.create(user=self.manager_user, role=RoleChoice.MANAGER.value, contact_number='1234567890')
        
        self.regular_user = User.objects.create_user(username='user', password='Riffat@1100')
        self.regular_profile = Profile.objects.create(user=self.regular_user, role=RoleChoice.DEVELOPER.value, contact_number='0987654321')
        
        self.project = Project.objects.create(
            title="Test Project",
            description="A project for testing",
            start_date="2024-07-27",
            end_date="2024-08-07"
        )
        self.project.team_members.set([self.regular_user.id]) 

        self.client.force_authenticate(user=self.manager_user)
        # self.client.force_authenticate(user=self.regular_user)

    def test_create_project(self):
        data = {
            "title": "Adding a New Project",
            "description": "Make separate git rep and add me in it",
            "start_date": "2024-07-27",
            "end_date": "2024-08-07",
            "team_members": [self.regular_user.id]
        }
        response = self.client.post('/api/projects/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_all_projects(self):
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_project(self):
        url = f'/api/projects/{self.project.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_project(self):
        url = f'/api/projects/{self.project.id}/'
        data = {
            "title": "Updated Title"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_project(self):
        url = f'/api/projects/{self.project.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TaskMethodsTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username='manager', password='testpass')
        self.manager_profile = Profile.objects.create(user=self.manager, role=RoleChoice.MANAGER.value)
        self.user = User.objects.create_user(username='user', password='testpass')
        self.user_profile = Profile.objects.create(user=self.user, role=RoleChoice.DEVELOPER.value)
        self.client = APIClient()
        self.client.force_authenticate(user=self.manager)
        self.project = Project.objects.create(title='Test Project', description='Test Description', start_date='2024-01-01', end_date='2024-12-31')
        self.project.team_members.set([self.user.id]) 
        self.task = Task.objects.create(title='Test Task', description='Test Task Description', status=StatusChoice.OPEN.value, project=self.project, assignee=self.user_profile)
        # self.client.force_authenticate(user=self.user)
    
    def test_create_task(self):
        data = {
            "title": "New Task",
            "description": "Task description",
            "status": "review",
            "project": self.project.id,
            "assignee": self.user_profile.id
        }
        response = self.client.post('/api/tasks/', data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_all_tasks(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_task_detail(self):
        url = f'/api/tasks/{self.task.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_task(self):
        updated_data = {
            'title': 'Updated Task Title',
        }
        response = self.client.put(f'/api/tasks/{self.task.id}/', data=updated_data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_task(self):
        url = f'/api/tasks/{self.task.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class DocumentMethodsTests(APITestCase):
    
    def setUp(self):
        self.manager_user = User.objects.create_user(username='manager', password='Riffat@1100')
        self.manager_profile = Profile.objects.create(user=self.manager_user, role=RoleChoice.MANAGER.value, contact_number='1234567890')
        
        self.regular_user = User.objects.create_user(username='regular', password='Riffat@1100')
        self.regular_profile = Profile.objects.create(user=self.regular_user, role=RoleChoice.DEVELOPER.value, contact_number='0987654321')

        self.project = Project.objects.create(
            title="Test Project",
            description="A project for testing",
            start_date="2024-07-27",
            end_date="2024-08-07"
        )
        self.project.team_members.set([self.regular_user.id]) 

        self.document = Document.objects.create(
            name='Test Document',
            description='Document for testing',
            version='1.0',
            project=self.project
        )
        self.client.force_authenticate(user=self.manager_user)
    
    def test_create_document(self):
        self.client.force_authenticate(user=self.manager_user)
        data = {
            "name": "New Document",
            "description": "Document description",
            "version": "2.0",
            "project": self.project.id
        }
        response = self.client.post('/api/documents/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_get_all_documents(self):
        response = self.client.get('/api/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_get_document(self):
        url = f'/api/documents/{self.document.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_document(self):
        url = f'/api/documents/{self.document.id}/'
        data = {
            "name": "Updated Document",
            "description": "Updated description",
        }
        response = self.client.put(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_delete_document(self):
        url = f'/api/documents/{self.document.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CommentMethodsTests(APITestCase):
    def setUp(self):
        self.manager_user = User.objects.create_user(username='anas', password='Riffat@1100')
        self.manager_profile = Profile.objects.create(user=self.manager_user, role=RoleChoice.MANAGER.value, contact_number='1234567890')
        
        self.regular_user = User.objects.create_user(username='user', password='Riffat@1100')
        self.regular_profile = Profile.objects.create(user=self.regular_user, role=RoleChoice.DEVELOPER.value, contact_number='0987654321')
        self.project = Project.objects.create(
            title="Test Project",
            description="A project for testing",
            start_date="2024-07-27",
            end_date="2024-08-07"
        )
        self.project.team_members.set([self.regular_profile.id]) 
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            status=StatusChoice.OPEN.value,
            project=self.project,
            assignee=self.regular_profile
        )
        self.comment = Comment.objects.create(
            text='Review the comments!',
            author=self.regular_user,
            project=self.project,
            task=self.task
        )
        self.client.force_authenticate(user=self.regular_user)

    def test_create_comment(self):
        url = '/api/comments/'
        data = {
            "text": "Review the comments!",
            "author": self.regular_user.id,
            "project": self.project.id,
            "task": self.task.id
        }
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_get_all_comments(self):
        url = '/api/comments/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_get_single_comment(self):
        url = f'/api/comments/{self.comment.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_update_comment(self):
        url = f'/api/comments/{self.comment.id}/'
        data = {
            "text": "Updated Comment Text"
        }
        response = self.client.put(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TimelineMethodTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.profile = Profile.objects.create(user=self.user, role=RoleChoice.MANAGER.value)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.project = Project.objects.create(title='Test Project', description='Test Description', start_date='2024-01-01', end_date='2024-12-31')
        self.timeline = Timeline.objects.get(project=self.project)

    def test_get_timeline(self):
        response = self.client.get('/api/timeline/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NotificationAPITestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.project = Project.objects.create(title='Test Project', description='Test Description', start_date='2024-01-01', end_date='2024-12-31')
        self.notification = Notification.objects.create(user=self.user, project=self.project, message='You have a new notification', is_read=False)
    
    def test_get_notifications(self):
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_mark_notification_read(self):
        response = self.client.put(f'/api/notifications/{self.notification.id}/mark_read/', data={'is_read': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


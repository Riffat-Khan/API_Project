from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .enum import RoleChoice, StatusChoice
from .models import Profile, Project, Task, Document, Comment, Timeline, Notification

User = get_user_model()

class ProfileMethodTests(APITestCase):

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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_exists = User.objects.filter(username="milli").exists()
        self.assertTrue(user_exists)
        
    def test_wrong_user_registration(self):
        data = {
            "username": "milli",
            "password": "Riffat@1100",
            "confirm_password": "1100",
            "profile": {
                "role": RoleChoice.QA.value,
                "contact_number": "3439887746764"
            }
        }
        response = self.client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProjectMethodsTests(APITestCase):

    def setUp(self):
        self.manager_user = User.objects.create_user(username='anas', password='Riffat@1100')
        self.manager_profile = Profile.objects.create(user=self.manager_user, role=RoleChoice.MANAGER.value, contact_number='1234567890')
        
        self.regular_user = User.objects.create_user(username='user', password='Riffat@1100')
        self.regular_profile = Profile.objects.create(user=self.regular_user, role=RoleChoice.DEVELOPER.value, contact_number='0987654321')
        
        self.project1 = Project.objects.create(
            title="Test Project",
            description="A project for testing",
            start_date="2024-07-27",
            end_date="2024-08-07"
        )
        self.project2 = Project.objects.create(
            title="Another Project",
            description="A project for testing",
            start_date="2024-07-27",
            end_date="2024-08-07"
        )
        self.client = APIClient()
        self.regular_client = APIClient()
        self.project1.team_members.set([self.regular_user.id]) 

        self.client.force_authenticate(user=self.manager_user)
        self.regular_client.force_authenticate(user=self.regular_user)

    def test_create_project(self):
        data = {
            "title": "Adding a New Project",
            "description": "Make separate git rep and add me in it",
            "start_date": "2024-02-27",
            "end_date": "2024-08-07",
            "team_members": [self.regular_user.id]
        }
        response = self.client.post('/api/projects/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project_exists = Project.objects.filter(title="Adding a New Project").exists()
        self.assertTrue(project_exists)
        
    def test_create_project_user(self):
        data = {
            "title": "Adding a New Project",
            "description": "Make separate git rep and add me in it",
            "start_date": "2024-07-27",
            "end_date": "2024-08-07",
            "team_members": [self.regular_user.id]
        }
        response = self.regular_client.post('/api/projects/', data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)
        
    def test_get_all_projects(self):
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) 

    def test_get_project(self):
        url = f'/api/projects/{self.project1.id}/'
        response = self.regular_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_project(self):
        url = f'/api/projects/{self.project1.id}/'
        data = {
            "title": "Updated Title"
        }
        response = self.client.put(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        projects = Project.objects.filter(title="Updated Title")
        self.assertEqual(projects.count(), 1)
        self.assertEqual(projects.first().title, "Updated Title")        
        
    def test_update_project_non_manager(self):
        url = f'/api/projects/{self.project1.id}/'
        data = {
            "title": "Updated Title"
        }
        response = self.regular_client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)

    def test_delete_project(self):
        url = f'/api/projects/{self.project1.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_project_non_manager(self):
        url = f'/api/projects/{self.project2.id}/'
        response = self.regular_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)


class TaskMethodsTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username='manager', password='testpass')
        self.manager_profile = Profile.objects.create(user=self.manager, role=RoleChoice.MANAGER.value)
        self.user = User.objects.create_user(username='user', password='testpass')
        self.user_profile = Profile.objects.create(user=self.user, role=RoleChoice.DEVELOPER.value)
        self.client = APIClient()
        self.regular_client = APIClient()
        self.client.force_authenticate(user=self.manager)
        self.project = Project.objects.create(title='Test Project', description='Test Description', start_date='2024-01-01', end_date='2024-12-31')
        self.project.team_members.set([self.user.id]) 
        self.task = Task.objects.create(title='Test Task', description='Test Task Description', status=StatusChoice.OPEN.value, project=self.project, assignee=self.user_profile)
        self.regular_client.force_authenticate(user=self.user)
    
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
        task_exists = Task.objects.filter(title="New Task").exists()
        self.assertTrue(task_exists)
        
    def test_create_task_non_manager(self):
        data = {
            "title": "New Task",
            "description": "Task description",
            "status": "review",
            "project": self.project.id,
            "assignee": self.user_profile.id
        }
        response = self.regular_client.post('/api/tasks/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)

    def test_get_all_tasks(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) 

    def test_get_task_detail(self):
        url = f'/api/tasks/{self.task.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5) 

    def test_update_task(self):
        updated_data = {
            'title': 'Updated Task Title',
        }
        response = self.client.put(f'/api/tasks/{self.task.id}/', data=updated_data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tasks = Project.objects.filter(title="Updated Task Title")
        self.assertEqual(tasks.count(), 1)
        self.assertEqual(tasks.first().title, "Updated Task Title")    
    
    def test_update_task(self):
        updated_data = {
            'title': 'Updated Task Title',
        }
        response = self.regular_client.put(f'/api/tasks/{self.task.id}/', data=updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_task(self):
        url = f'/api/tasks/{self.task.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
    def test_delete_task_non_manager(self):
        url = f'/api/tasks/{self.task.id}/'
        response = self.regular_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentMethodsTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='anas', password='Riffat@1100')
        self.author_profile = Profile.objects.create(user=self.user1, role=RoleChoice.MANAGER.value, contact_number='1234567890')
        
        self.regular_user = User.objects.create_user(username='user', password='Riffat@1100')
        self.regular_profile = Profile.objects.create(user=self.regular_user, role=RoleChoice.DEVELOPER.value, contact_number='0987654321')
        self.project = Project.objects.create(
            title="Test Project",
            description="A project for testing",
            start_date="2024-07-27",
            end_date="2024-08-07"
        )
        self.project.team_members.set([self.author_profile.id]) 
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            status=StatusChoice.OPEN.value,
            project=self.project,
            assignee=self.author_profilope
        )
        self.comment = Comment.objects.create(
            text='Review the comment!',
            author=self.user1,
            project=self.project,
            task=self.task
        )
        self.client.force_authenticate(user=self.user1)

    def test_create_comment(self):
        url = '/api/comments/'
        data = {
            "text": "Review the comments!",
            "author": self.author_profile.id,
            "project": self.project.id,
            "task": self.task.id
        }
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment_exists = Comment.objects.filter(text="Review the comments!").exists()
        self.assertTrue(comment_exists)
        
    def test_get_all_comments(self):
        url = '/api/comments/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) 
        
    def test_get_single_comment(self):
        url = f'/api/comments/{self.comment.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5) 
        
    def test_update_comment(self):
        url = f'/api/comments/{self.comment.id}/'
        data = {
            "text": "Updated Comment Text"
        }
        response = self.client.put(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_update_others_comment(self):
        self.client.force_authenticate(self.regular_user)
        url = f'/api/comments/{self.comment.id}/'
        data = {
            "text": "Updated Comment Text"
        }
        response = self.client.put(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_delete_comment(self):
        url = f'/api/comments/{self.comment.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
    def test_delete_others_comment(self):
        self.client.force_authenticate(self.regular_user)
        url = f'/api/comments/{self.comment.id}/'
        response = self.client.delete(url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_delete_non_existent_comment(self):
        non_existent_id = 100
        url = f'/api/comments/{non_existent_id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



class DocumentMethodsTests(APITestCase):
    
    def setUp(self):
        self.user1 = User.objects.create_user(username='member', password='Riffat@1100')
        self.member_profile = Profile.objects.create(user=self.user1, role=RoleChoice.DEVELOPER.value, contact_number='1234567890')
        
        self.user2 = User.objects.create_user(username='regular', password='Riffat@1100')
        self.regular_profile = Profile.objects.create(user=self.user2, role=RoleChoice.DEVELOPER.value, contact_number='0987654321')

        self.project = Project.objects.create(
            title="Test Project",
            description="A project for testing",
            start_date="2024-07-27",
            end_date="2024-08-07"
        )
        self.project.team_members.set([self.user1.id]) 

        self.task = Task.objects.create(title='Test Task', description='Test Task Description', status=StatusChoice.OPEN.value, project=self.project, assignee=self.member_profile)
        
        self.document = Document.objects.create(
            name='Test Document',
            description='Document for testing',
            version='1.0',
            project=self.project
        )
        self.client.force_authenticate(user=self.user1)
    
    def test_create_document(self):
        data = {
            "name": "New Document",
            "description": "Document description",
            "version": "2.0",
            "project": self.project.id
        }
        response = self.client.post('/api/documents/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        doc_exists = Document.objects.filter(name="New Document").exists()
        self.assertTrue(doc_exists)

    def test_get_all_documents(self):
        response = self.client.get('/api/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) 
    
    def test_get_all_documents_non_manager(self):
        self.client.force_authenticate(self.user2)
        response = self.client.get('/api/documents/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_get_document(self):
        url = f'/api/documents/{self.document.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5) 
        
    def test_get_non_existent_document(self):
        non_existent_id = 100
        url = f'/api/documents/{non_existent_id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_document(self):
        url = f'/api/documents/{self.document.id}/'
        data = {
            "name": "Updated Document",
            "description": "Updated description",
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doc = Document.objects.filter(name="Updated Document")
        self.assertEqual(doc.count(), 1)
        self.assertEqual(doc.first().name, "Updated Document")
        
    def test_update_non_existent_document(self):
        non_existent_id = 100
        url = f'/api/documents/{non_existent_id}/'
        data = {
            "name": "Updated Document",
            "description": "Updated description",
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_delete_document(self):
        url = f'/api/documents/{self.document.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_delete_non_existent_document(self):
        non_existent_id = 100
        url = f'/api/documents/{non_existent_id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    


class TimelineMethodTestCase(APITestCase):
    
    def setUp(self):
        self.manager = User.objects.create_user(username='testuser', password='testpass')
        self.profile_manager = Profile.objects.create(user=self.manager, role=RoleChoice.MANAGER.value)
        self.user = User.objects.create_user(username='user', password='testpass')
        self.profile_user = Profile.objects.create(user=self.user, role=RoleChoice.DEVELOPER.value)
        self.client = APIClient()
        self.client.force_authenticate(user=self.manager)
        self.project = Project.objects.create(title='Test Project', description='Test Description', start_date='2024-01-01', end_date='2024-12-31')
        self.timeline = Timeline.objects.get(project=self.project)

    def test_get_timeline(self):
        response = self.client.get('/api/timeline/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1) 
        
    def test_get_timeline_not_manager(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/timeline/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class NotificationAPITestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user2 = User.objects.create_user(username='user2', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.project = Project.objects.create(title='Test Project', description='Test Description', start_date='2024-01-01', end_date='2024-12-31')
        self.notification = Notification.objects.create(user=self.user, project=self.project, message='You have a new notification', is_read=False)
        self.notification2 = Notification.objects.create(user=self.user2, project=self.project, message='You have a new notification', is_read=False)

    def test_get_notifications(self):
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notifications = response.json()
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0]['message'], 'You have a new notification')
    
    def test_get_other_other_users_notification(self):
        response = self.client.put(f'/api/notifications/{self.notification2.id}/mark_read/', data={'is_read': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_mark_notification_read(self):
        response = self.client.put(f'/api/notifications/{self.notification.id}/mark_read/', data={'is_read': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)


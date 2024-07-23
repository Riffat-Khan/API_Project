from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
   

class UserRegistrationTestCase(APITestCase):
    def test_user_registration(self):
        url = reverse('register')
        data = {
            "username": "hanzala",
            "password": "Riffat@1100"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        

class UserLoginTestCase(APITestCase):
    def setUp(self):
        self.username = 'jaweria'
        self.password = 'Riffat@1100'
        User.objects.create_user(username=self.username, password=self.password)
        
    def test_user_login(self):
        url = reverse('login')
        data = {
            "username": self.username,
            "password": self.password
        }
        response = self.client.post(url, data, format='json')
        print(response.data)  # Print response data for debugging
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        

class UserLogoutTestCase(APITestCase):
    def setUp(self):
        self.username = 'jasmine'
        self.password = 'Riffat@1100'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.token = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.token)
        
    def test_user_logout(self):
        url = reverse('logout')
        data = {
            "refresh": self.refresh_token
        }
        response = self.client.post(url, data, format='json', HTTP_AUTHORIZATION='Bearer ' + str(self.token.access_token))
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(response.data['message'], 'Logout successful')
     
        
        

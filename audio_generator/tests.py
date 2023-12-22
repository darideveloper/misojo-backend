from . import models
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase


class TestUser (APITestCase):
    """ Test user model: create """
    
    def setUp(self):
        self.client = APIClient()
        
        # Default url pattern
        self.url = reverse('users-list')
        
        self.data = {
            "first_name": "sample name",
            "last_name": "sample pass",
            "password": "12345678",
            "email": "sample@mail.com"
        }
    
    def __create_user__(self):
        """ Create user with request and validate api response """
        
        # Request to create new user
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'User created successfully')
        self.assertEqual(response.data['data'], {})
     
    def test_post(self):
        """ Try to create user with valid data
            Expected 200: user created successfully and email send
        """
        
        # Send request and validate response
        self.__create_user__()
        
        # Validate user in database
        user = models.User.objects.filter(email=self.data['email'])
        self.assertEqual(user.count(), 1)
        user = user.first()
        
        # Validate is_active and is_admin status
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_admin)
        
        # Validate email sent
        self.assertEqual(len(mail.outbox), 1)
        
    def test_missing_fields(self):
        """ Try to create user with missing fields
            Expected 400: error response
        """
        
        self.data.pop('first_name')
        
        # Request with invalid data
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('is required', response.data['message'])
        self.assertIn('first name', response.data['message'])
        self.assertIn('first_name', response.data['data'])
        
        # Validate user no created in database
        user = models.User.objects.filter(email=self.data['email'])
        self.assertEqual(user.count(), 0)

    def test_already_used_email(self):
        """ Try to create a user with an email already used
            Expected 400: error response
        """
        
        # Send request and validate response
        self.__create_user__()
        
        # Send second request with the same email
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(
            response.data['message'],
            'email error: user with this email already exists'
        )
        self.assertIn('email', response.data['data'])
        
        # Validate user no created in database
        user = models.User.objects.filter(email=self.data['email'])
        self.assertEqual(user.count(), 1)
        
    def test_short_password(self):
        """ Try to create a user with a short password
            Expected 400: error response
        """
        
        self.data['password'] = '1234567'
        
        # Send request and validate response
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(
            response.data['message'],
            'password error: password must be at least 8 characters'
        )
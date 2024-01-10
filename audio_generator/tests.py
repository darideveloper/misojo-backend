from . import models
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase


class TestUser (APITestCase):
    """ Test user model: create """
    
    def setUp(self):
        """ Save default data """
        
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
        self.assertEqual(response.data['message'], 'API.REGISTER.CREATED')
     
    def test_created(self):
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
        
    def test_missing_data(self):
        """ Try to create user with missing fields
            Expected 400: error response
        """
        
        self.data.pop('first_name')
        
        # Request with invalid data
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('is required', response.data['message'])
        self.assertIn('first_name', response.data['message'])
        self.assertIn('first_name', response.data['data'])
        
        # Validate user no created in database
        user = models.User.objects.filter(email=self.data['email'])
        self.assertEqual(user.count(), 0)

    def test_duplicated(self):
        """ Try to create a user with an email already used
            Expected 400: error response
        """
        
        # Send request and validate response
        self.__create_user__()
        
        # Send second request with the same email
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'API.REGISTER.DUPLICATED')
        self.assertIn('email', response.data['data'])
        
        # Validate user no created in database
        user = models.User.objects.filter(email=self.data['email'])
        self.assertEqual(user.count(), 1)
        
    def test_invalid_password(self):
        """ Try to create a user with a short password
            Expected 400: error response
        """
        
        self.data['password'] = '1234567'
        
        # Send request and validate response
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'API.REGISTER.INVALID_PASSWORD')
        
        
class TestToken(APITestCase):
    """ Test get JWT token """
    
    def setUp(self):
        """ Register and activate user """
        
        self.client = APIClient()
        
        # Default url pattern
        self.url = reverse('token_obtain_pair')
        
        # Create user
        password = '12345678'
        self.user = models.User.objects.create_user(
            email="sample@gmail.com",
            first_name='sample name',
            last_name='sample last name',
            password=password
        )
        
        # Activate user
        self.user.is_active = True
        self.user.save()
        
        self.data = {
            "email": self.user.email,
            "password": password
        }
    
    def __test_invalid_user__(self, data: dict):
        """ Try to get token with invalid credentials
            Expected 400: error response
        """
        
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'API.TOKEN.INVALID_CRED')
    
    def test_generated(self):
        """ Try to generate token with valid credentials
            Expected 200: token generated
        """
        
        # Request with valid credentials
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('access', response.data["data"])
        self.assertIn('refresh', response.data["data"])
        
    def test_invalid_cred_email(self):
        """ Try to generate token with invalid email
            Expected 400: error response
        """
        
        # Request with valid credentials
        self.data["email"] = "invalid email"
        self.__test_invalid_user__(self.data)
        
    def test_invalid_cred_password(self):
        """ Try to generate token with invalid password
            Expected 400: error response
        """
        
        # Request with valid credentials
        self.data["password"] = "invalid password"
        self.__test_invalid_user__(self.data)
    
    def test_inactive(self):
        """ Try to generate token with inactive user
            Expected 400: error response
        """
        
        # Deactivate user
        self.user.is_active = False
        self.user.save()
        
        # Request with valid credentials
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'API.TOKEN.INACTIVE')


class TestTokenRefresh(APITestCase):
    """ Test refresh JWT token """
    
    def setUp(self) -> None:
        """ Register and activate user """
        self.client = APIClient()
        
        # Default url pattern
        self.url = reverse('token_refresh')
        
        # Create user
        self.email = "sample@gmail.com"
        self.password = '12345678'
        user = models.User.objects.create_user(
            email=self.email,
            first_name='sample',
            last_name='sample',
            password=self.password
        )
        user.is_active = True
        user.save()
        
    def test_refreshed(self):
        """ Try to refresh token with valid refresh token
            Expected 200: success response
        """
        
        # Send post request to get initial token
        response = self.client.post(reverse('token_obtain_pair'), {
            "email": self.email,
            "password": self.password
        })
        access = response.data['data']['access']
        refresh = response.data['data']['refresh']
                
        # Validate response content
        response = self.client.post(self.url, {"refresh": refresh})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('access', response.data["data"])
        self.assertIn('refresh', response.data["data"])
        
        # Validate new tokens
        self.assertNotEqual(access, response.data["data"]["access"])
        self.assertNotEqual(refresh, response.data["data"]["refresh"])
        
        # Validate refresh token blacklisted, try to refresh again
        response = self.client.post(self.url, {"refresh": refresh})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], "Token is blacklisted")
        self.assertNotIn('access', response.data["data"])
        self.assertNotIn('refresh', response.data["data"])
        
    def test_invalid_token(self):
        """ Try to refresh token with invalid refresh token
            Expected 401: error response
        """
        
        response = self.client.post(self.url, {"refresh": "fake token 123"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], "Token is invalid or expired")
        self.assertNotIn('access', response.data["data"])
        self.assertNotIn('refresh', response.data["data"])
        
    def test_missing_data(self):
        """ Try to refresh token without refresh token
            Expected 401: error response
        """
        
        # Request without token
        response = self.client.post(self.url)
        
        # Validate response content
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('refresh', response.data['message'])
        self.assertIn('is required', response.data['message'])
        self.assertNotIn('access', response.data["data"])
                       
        
class TestValidateToken(APITestCase):
    """ Test validate token """
    
    def setUp(self):
        """ Register user and get token """
        self.client = APIClient()
        
        # Default url pattern
        self.url = reverse('validate_token')
        
        # Create user
        email = "sample@gmail.com"
        password = '12345678'
        user = models.User.objects.create_user(
            email=email,
            first_name='sample',
            last_name='sample',
            password=password
        )
        user.is_active = True
        user.save()
        
        # Send post request to get token
        response = self.client.post(reverse('token_obtain_pair'), {
            "email": email,
            "password": password
        })
        self.token = response.data['data']['access']
        
    def test_missing_data(self):
        """ Try to validate token without token
            Expected 401: error response
        """
        
        # Request without token
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(
            response.data['message'],
            'Authentication credentials were not provided.'
        )
        
    def test_invalid_token(self):
        """ Try to validate token with invalid token
            Expected 401: error response
        """
        
        # Request with invalid token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(
            response.data['message'],
            'Given token not valid for any token type'
        )
        
    def test_invalid_format(self):
        """ Try to validate token with invalid token json format
            Expected 401: error response
        """
        
        # Request with invalid token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid token')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(
            response.data['message'],
            'Authorization header must contain two space-delimited values'
        )
        
    def test_valid(self):
        """ Try to validate token with valid token
            Expected 200: success response
        """
        
        # Request with valid token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Token is valid')
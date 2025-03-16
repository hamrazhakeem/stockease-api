from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User
from .utils.redis_utils import store_user_data, get_user_data
import json
from unittest.mock import patch

class AccountsAPITestCase(TestCase):
    """Test suite for the Accounts API."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            email='existing@example.com',
            password='existingpassword123'
        )
        
        # Set up API client
        self.client = APIClient()
    
    @patch('accounts.views.send_otp_email')
    def test_user_signup(self, mock_send_email):
        """Test user signup process."""
        # Mock the email sending function
        mock_send_email.return_value = True
        
        # Test signup with new email
        signup_data = {
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'password2': 'newpassword123'
        }
        
        response = self.client.post(reverse('signup'), signup_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('message', response.data)
        
        # Verify email was "sent"
        mock_send_email.assert_called_once()
        
        # Store token for OTP verification
        self.signup_token = response.data['token']
    
    @patch('accounts.views.send_otp_email')
    def test_signup_existing_email(self, mock_send_email):
        """Test signup with existing email."""
        signup_data = {
            'email': 'existing@example.com',
            'password': 'newpassword123',
            'password2': 'newpassword123'
        }
        
        response = self.client.post(reverse('signup'), signup_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
        # Verify email was not sent
        mock_send_email.assert_not_called()
    
    @patch('accounts.views.send_otp_email')
    def test_otp_verification(self, mock_send_email):
        """Test OTP verification process."""
        # Mock the email sending function
        mock_send_email.return_value = True
        
        # First sign up
        signup_data = {
            'email': 'otptest@example.com',
            'password': 'otppassword123',
            'password2': 'otppassword123'
        }
        
        signup_response = self.client.post(reverse('signup'), signup_data, format='json')
        token = signup_response.data['token']
        
        # Get the OTP from Redis (we need to extract it from the mocked function)
        user_data = get_user_data(token)
        otp = user_data['otp']
        
        # Verify OTP
        verification_data = {
            'token': token,
            'otp': otp
        }
        
        response = self.client.post(reverse('verify_otp'), verification_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
        
        # Verify user was created
        self.assertTrue(User.objects.filter(email='otptest@example.com').exists())
    
    def test_invalid_otp(self):
        """Test verification with invalid OTP."""
        # First sign up and get token
        with patch('accounts.views.send_otp_email') as mock_send_email:
            mock_send_email.return_value = True
            
            signup_data = {
                'email': 'invalidotp@example.com',
                'password': 'invalidpassword123',
                'password2': 'invalidpassword123'
            }
            
            signup_response = self.client.post(reverse('signup'), signup_data, format='json')
            token = signup_response.data['token']
        
        # Try with invalid OTP
        verification_data = {
            'token': token,
            'otp': '999999'  # Incorrect OTP
        }
        
        response = self.client.post(reverse('verify_otp'), verification_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('otp', response.data)
        
        # Verify user was not created
        self.assertFalse(User.objects.filter(email='invalidotp@example.com').exists())
    
    def test_user_login(self):
        """Test user login."""
        login_data = {
            'email': 'existing@example.com',
            'password': 'existingpassword123'
        }
        
        response = self.client.post(reverse('login'), login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
        
        # Store tokens for logout test
        self.refresh_token = response.data['tokens']['refresh']
        self.access_token = response.data['tokens']['access']
    
    def test_invalid_login(self):
        """Test login with invalid credentials."""
        # Test with wrong password
        login_data = {
            'email': 'existing@example.com',
            'password': 'wrongpassword123'
        }
        
        response = self.client.post(reverse('login'), login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test with non-existent email
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'somepassword123'
        }
        
        response = self.client.post(reverse('login'), login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_logout(self):
        """Test user logout."""
        # First login to get tokens
        login_data = {
            'email': 'existing@example.com',
            'password': 'existingpassword123'
        }
        
        login_response = self.client.post(reverse('login'), login_data, format='json')
        refresh_token = login_response.data['tokens']['refresh']
        access_token = login_response.data['tokens']['access']
        
        # Authenticate for logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Logout
        logout_data = {
            'refresh': refresh_token
        }
        
        response = self.client.post(reverse('logout'), logout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Try to use the refresh token (should fail)
        refresh_data = {
            'refresh': refresh_token
        }
        
        response = self.client.post(reverse('token_refresh'), refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_email(self):
        """Test updating user email."""
        # First login
        login_data = {
            'email': 'existing@example.com',
            'password': 'existingpassword123'
        }
        
        login_response = self.client.post(reverse('login'), login_data, format='json')
        access_token = login_response.data['tokens']['access']
        
        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Update email
        update_data = {
            'email': 'updated@example.com'
        }
        
        response = self.client.put(reverse('update_email'), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'updated@example.com')
        
        # Verify email was updated in database
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')
    
    def test_change_password(self):
        """Test changing user password."""
        # First login
        login_data = {
            'email': 'existing@example.com',
            'password': 'existingpassword123'
        }
        
        login_response = self.client.post(reverse('login'), login_data, format='json')
        access_token = login_response.data['tokens']['access']
        
        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Change password
        password_data = {
            'current_password': 'existingpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        }
        
        response = self.client.put(reverse('change_password'), password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify by logging in with new password
        self.client.credentials()  # Clear credentials
        
        new_login_data = {
            'email': 'existing@example.com',
            'password': 'newpassword456'
        }
        
        response = self.client.post(reverse('login'), new_login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_profile(self):
        """Test retrieving user profile."""
        # First login
        login_data = {
            'email': 'existing@example.com',
            'password': 'existingpassword123'
        }
        
        login_response = self.client.post(reverse('login'), login_data, format='json')
        access_token = login_response.data['tokens']['access']
        user_id = login_response.data['user']['id']
        
        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Get profile
        response = self.client.get(reverse('user_details', args=[user_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'existing@example.com')
    
    def test_unauthorized_profile_access(self):
        """Test that users cannot access other users' profiles."""
        # Create another user
        other_user = User.objects.create_user(
            email='other@example.com',
            password='otherpassword123'
        )
        
        # Login as original user
        login_data = {
            'email': 'existing@example.com',
            'password': 'existingpassword123'
        }
        
        login_response = self.client.post(reverse('login'), login_data, format='json')
        access_token = login_response.data['tokens']['access']
        
        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Try to access other user's profile
        response = self.client.get(reverse('user_details', args=[other_user.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

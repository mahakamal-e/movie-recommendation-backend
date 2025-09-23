"""
tests.py

Unit tests for user management and authentication API endpoints.

"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User


class UserTests(APITestCase):
    """
    Test suite for User registration, login, and profile endpoints.
    """

    def setUp(self):
        """
        Set up a test user and API endpoint URLs.
        """
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="TestPassword123!"
        )
        self.register_url = reverse("auth_register")
        self.token_url = reverse("token_obtain_pair")
        self.me_url = reverse("users_me")

    def test_register_user(self):
        """
        Test that a new user can register successfully.

        Verifies:
        - HTTP 201 response
        - User count increment
        - Email saved correctly
        """
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!",
            "first_name": "New",
            "last_name": "User"
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(username="newuser").email, "newuser@example.com")

    def test_register_password_mismatch(self):
        """
        Test registration failure when passwords do not match.

        Verifies:
        - HTTP 400 response
        - Error key 'password' in response
        """
        data = {
            "username": "newuser2",
            "email": "newuser2@example.com",
            "password": "Password123!",
            "password2": "Password1234!",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_login_with_username(self):
        """
        Test JWT login using username.

        Verifies:
        - HTTP 200 response
        - Access and refresh tokens returned
        - Correct user email in response
        """
        data = {"username": "testuser", "password": "TestPassword123!"}
        response = self.client.post(self.token_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "testuser@example.com")

    def test_login_with_email(self):
        """
        Test JWT login using email.

        Verifies:
        - HTTP 200 response
        - Access and refresh tokens returned
        - Correct username in response
        """
        data = {"username": "testuser@example.com", "password": "TestPassword123!"}
        response = self.client.post(self.token_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["username"], "testuser")

    def test_login_fail_wrong_credentials(self):
        """
        Test login failure with incorrect password.

        Verifies:
        - HTTP 400 response
        """
        data = {"username": "testuser", "password": "WrongPassword!"}
        response = self.client.post(self.token_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_me_authenticated(self):
        """
        Test retrieving current user's profile when authenticated.

        Steps:
        - Login to get JWT token
        - Access /users/me/ endpoint with token

        Verifies:
        - HTTP 200 response
        - Correct username and email returned
        """
        # Obtain token
        response = self.client.post(
            self.token_url,
            {"username": "testuser", "password": "TestPassword123!"},
            format="json"
        )
        access_token = response.data["access"]

        # Set credentials
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "testuser@example.com")

    def test_get_me_unauthenticated(self):
        """
        Test accessing /users/me/ without authentication token.

        Verifies:
        - HTTP 401 response
        """
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

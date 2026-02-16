from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

# Create your tests here.
REGISTER_URL = reverse("users:create")
TOKEN_URL = reverse("users:token_obtain_pair")
ME_URL = reverse("users:manage")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class UserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user with valid payload is successful"""
        payload = {
            "email": "test@test.com",
            "password": "testpassword123",
        }
        res = self.client.post(REGISTER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

    def test_user_already_exists(self):
        """Test creating a user with an email that already exists fails"""
        payload = {
            "email": "test@test.com",
            "password": "testpassword123",
        }
        create_user(**payload)

        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_obtain_pair(self):
        """Test that we can get a JWT token"""
        payload = {
            "email": "test@test.com",
            "password": "testpassword123",
        }
        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_manage_user_authentication_required(self):
        """Test that authentication is required for managing user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="admin@test.com",
            password="testpassword123",
        )

        res = self.client.post(TOKEN_URL, {
            "email": "admin@test.com",
            "password": "testpassword123",
        })
        self.token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZE="Bearer " + self.token)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)

    def test_update_profile_success(self):
        """Test updating user profile"""
        payload = {
            "password": "newPassword123",
            "email": "newemail@test.com"
        }
        res = self.client.patch(ME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, payload["email"])
        self.assertTrue(self.user.check_password(payload["password"]))

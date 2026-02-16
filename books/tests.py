from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book

BOOK_URL = reverse("books:book-list")


def sample_book(**params):
    defaults = {
        "title": "Default Title",
        "author": "Default Author",
        "cover": "HARD",
        "inventory": 10,
        "daily_fee": 5.50,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


class UnauthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is NOT required for list"""
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpassword123"
        )
        self.client.force_authenticate(self.user)

    def test_list_books(self):
        """Test that authenticated user can see books"""
        sample_book()
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_book_forbidden(self):
        """Test that standard user CANNOT create a book"""
        payload = {
            "title": "New Book",
            "author": "New Author",
            "cover": "Hard",
            "inventory": 10,
            "daily_fee": 5.00,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book(self):
        """Test that standard user CAN NOT delete a book"""
        book = sample_book()
        url = reverse("books:book-detail", args=[book.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@test.com", password="testpassword123"
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        """Test that admin user CAN create a book"""
        payload = {
            "title": "New Book",
            "author": "New Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": 5.00,
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_book(self):
        """Test that admin user CAN delete a book"""
        book = sample_book()
        url = reverse("books:book-detail", args=[book.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

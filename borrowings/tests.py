import datetime

from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer

BORROWING_URL = reverse("borrowings:borrowing-list")


def sample_book(**params):
    defaults = {
        "title": "Sample book",
        "author": "Sample author",
        "cover": "Hard",
        "inventory": 10,
        "daily_fee": 10.50,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def sample_borrowing(user, book, **params):
    defaults = {
        "expected_return_date": timezone.now().date() + datetime.timedelta(days=1),
    }
    defaults.update(params)
    return Borrowing.objects.create(user=user, book=book, **defaults)


# Create your tests here.
class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpassword123"
        )
        self.client.force_authenticate(self.user)
        self.book = sample_book()

    def test_list_borrowings(self):
        """Test listing borrowings for authenticated user"""
        sample_borrowing(user=self.user, book=self.book)
        other_user = get_user_model().objects.create_user(
            email="other@test.com", password="testpassword123"
        )
        sample_borrowing(user=other_user, book=self.book)

        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.filter(user=self.user.id)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing(self):
        """Test creating a new borrowing"""
        payload = {
            "book": self.book.id,
            "expected_return_date": (timezone.now() + datetime.timedelta(days=7)).date()
        }
        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        borrowing = Borrowing.objects.get(id=res.data["id"])

        self.assertEqual(payload["book"], borrowing.book.id)
        self.assertEqual(
            payload["expected_return_date"],
            borrowing.expected_return_date
        )
        self.assertEqual(borrowing.user, self.user)

    def test_borrowing_decreases_inventory(self):

        book = sample_book(inventory=6)

        payload = {
            "book": book.id,
            "expected_return_date": (timezone.now() + datetime.timedelta(days=7)).date()
        }

        res = self.client.post(BORROWING_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        book.refresh_from_db()

        self.assertEqual(book.inventory, 5)

    def test_borrowing_failed_if_inventory_zero(self):

        book = sample_book(inventory=0)

        payload = {
            "book": book.id,
            "expected_return_date": (
                    timezone.now() + datetime.timedelta(days=7)
            ).date()
        }

        res = self.client.post(BORROWING_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("book", res.data)

    def test_borrowing_date_constraint(self):
        """Test that expected_return_date cannot be earlier than borrow_date"""
        with self.assertRaises(IntegrityError):
            Borrowing.objects.create(
                user=self.user,
                book=self.book,
                expected_return_date=timezone.now().date() - datetime.timedelta(days=1)
            )

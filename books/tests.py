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


class BookAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.book = sample_book(title="Test Book")
        self.detail_url = reverse("books:book-detail", args=[self.book.id])

    def test_list_books(self):
        """Test retrieving a list of books"""
        sample_book(title="Second Book")

        res = self.client.get(BOOK_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_create_book(self):
        """Test creating a new book"""
        payload = {
            "title": "Good Book",
            "author": "Sigma",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": 2.00,
        }

        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = Book.objects.filter(title=payload["title"]).exists()
        self.assertTrue(exists)

    def test_retrieve_book_detail(self):
        """Test retrieving specific book detail"""
        res = self.client.get(self.detail_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["title"], self.book.title)

    def test_update_book_partial(self):
        """Test updating book with PATCH"""
        payload = {
            "title": "Updated Title",
            "cover": "SOFT",
        }
        res = self.client.patch(self.detail_url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Updated Title")
        self.assertEqual(self.book.cover, "SOFT")

        self.assertEqual(self.book.author, "Default Author")

    def test_delete_book(self):
        """Test deleting a book"""
        res = self.client.delete(self.detail_url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())
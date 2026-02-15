from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

PAYMENT_URL = reverse("payments:payment-list")


def sample_payment(user, **params):
    book = Book.objects.create(
        title=f"Test Book {user.id}",
        author="Test Author",
        cover="HARD",
        inventory=10,
        daily_fee=Decimal("5.00")
    )
    borrowing = Borrowing.objects.create(
        user=user,
        book=book,
        expected_return_date="2027-01-01",
    )

    defaults = {
        "status": "PENDING",
        "type": "PAYMENT",
        "borrowing": borrowing,
        "money_to_pay": Decimal("10.50"),
        "session_url": "https://stripe.com/pay",
        "session_id": f"sess_{user.id}_12345"
    }
    defaults.update(params)

    return Payment.objects.create(**defaults)


class UnauthenticatedPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to access payments list."""
        res = self.client.get(PAYMENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpassword123"
        )
        self.client.force_authenticate(self.user)

    def test_list_payment_sees_only_own(self):
        """Test that an authenticated user can see only their own payments."""
        payment1 = sample_payment(user=self.user)

        other_user = get_user_model().objects.create_user(
            email="rakushka23@gmail.com", password="paswrod234"
        )
        payment2 = sample_payment(user=other_user)

        res = self.client.get(PAYMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # User should see only 1 payment (their own)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["id"], payment1.id)

    def test_modification_forbidden(self):
        """Test that a standard user cannot modify or delete payments (Method Not Allowed)."""
        payment = sample_payment(user=self.user)
        url = reverse("payments:payment-detail", args=[payment.id])

        # Try to DELETE
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Try to UPDATE (PUT)
        payload = {"status": "PAID"}
        res_put = self.client.put(url, payload)
        self.assertEqual(
            res_put.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )


class AdminPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@test.com", password="testpassword123"
        )
        self.client.force_authenticate(self.user)

    def test_list_sees_all_payments(self):
        """Test that an admin user can see payments from all users."""
        sample_payment(user=self.user)  # Admin's payment

        other_user = get_user_model().objects.create_user(
            email="usertest@gmail.com", password="toohardpass23"
        )
        sample_payment(user=other_user)  # Other user's payment

        res = self.client.get(PAYMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Admin should see BOTH payments (2 total)
        self.assertEqual(len(res.data["results"]), 2)

    def test_payment_modification_forbidden(self):
        """Test that even an admin cannot modify or delete payments via API."""
        payment = sample_payment(user=self.user)
        url = reverse("payments:payment-detail", args=[payment.id])

        # Test DELETE
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test UPDATE
        payload = {"status": "PAID"}
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

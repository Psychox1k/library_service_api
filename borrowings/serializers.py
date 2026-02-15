from django.db import transaction
from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing
from payments.serializer import PaymentSerializer
from payments.utils import create_payment_session
from payments.models import Payment


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )
        read_only_fields = ("id", "borrow_date", "actual_return_date")

    def validate(self, attrs):
        data = super().validate(attrs)
        book = data["book"]

        if book.inventory <= 0:
            raise serializers.ValidationError({
                "book": "Inventory is empty for this book"
            })

        requests = self.context.get("request")

        if requests and requests.user.is_authenticated:
            has_pending_payments = Payment.objects.filter(
                borrowing__user=requests.user,
                status="PENDING"
            ).exists()

            if has_pending_payments:
                raise serializers.ValidationError(
                    "You have pending payments! Pay them first before borrowing new books"
                )

        return data

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data["book"]
            book.inventory -= 1
            book.save()

            borrowing = super().create(validated_data)
            create_payment_session(borrowing)

        return borrowing


class BorrowingListSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)

    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    book = serializers.CharField(source="book.title", read_only=True)
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "payments"
        )

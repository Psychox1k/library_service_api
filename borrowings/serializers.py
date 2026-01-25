from django.db import transaction
from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing


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
        return data

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data["book"]
            book.inventory -= 1
            book.save()

        return super().create(validated_data)


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

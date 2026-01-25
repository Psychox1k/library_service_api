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

        return data

    def create(self, validated_data):
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
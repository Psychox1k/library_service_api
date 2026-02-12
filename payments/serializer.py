from rest_framework import serializers
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "status", "type", "session_url", "session_id", "money_to_pay")

        read_only_fields = ("session_url", "session_id")


class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "status", "type", "money_to_pay", "borrowing")


class PaymentDetailSerializer(PaymentSerializer):
    book_title = serializers.CharField(source="borrowing.book.title", read_only=True)
    user_email = serializers.CharField(source="borrowing.user.email", read_only=True)

    class Meta:
        model = Payment
        fiedls = (
            "id", "status", "type", "borrowing",
            "session_url", "session_id", "money_to_pay",
            "book_title", "user_email"
        )
import os

import stripe
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from payments.models import Payment
from payments.serializer import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer
)
from payments.utils import create_stripe_session

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


# Create your views here.
class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.select_related("borrowing__user", "borrowing__book")
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(borrowing__user=user)

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer

        return PaymentSerializer

    @action(detail=True, methods=["POST"], url_path="renew")
    def renew_payment(self, request, pk=None):

        payment = self.get_object()

        if payment.status != "EXPIRED":
            return Response({"detail": "Payment is not expired. You cannt renew it."},
                            status.HTTP_400_BAD_REQUEST)

        borrowing = payment.borrowing

        duration = borrowing.expected_return_date - borrowing.borrow_date
        days = max(duration.days, 1)
        total_price = int(days * borrowing.book.daily_fee * 100)

        try:

            new_session = create_stripe_session(borrowing)

            payment.status = "PENDING"
            payment.session_id = new_session.id
            payment.session_url = new_session.url
            payment.save()

            return Response(
                {"session_url": payment.session_url},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

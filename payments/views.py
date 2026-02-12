from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from payments.models import Payment
from payments.serializer import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer
)


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

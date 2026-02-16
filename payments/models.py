from django.db import models
from borrowings.models import Borrowing


# Create your models here.
class Payment(models.Model):

    class StatusType(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        EXPIRED = "EXPIRED", "Expired"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT", "Payment"
        FINE = "FINE", "Fine"

    status = models.CharField(max_length=7, choices=StatusType.choices)
    type = models.CharField(max_length=7, choices=Type.choices)

    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    session_url = models.URLField(max_length=500, blank=True, null=True)
    session_id = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True
    )

    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return (f"{self.get_type_display()} for Borrowing"
                f" {self.borrowing.id} ({self.get_status_display()}")

from django.contrib import admin

from payments.models import Payment


# Register your models here.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "type", "borrowing", "money_to_pay")
    list_filter = ("status", "type")
    search_fields = ("session_id",)

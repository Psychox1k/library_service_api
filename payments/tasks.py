import stripe
import os
from celery import shared_task
from .models import Payment

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


@shared_task()
def check_pending_payments():
    """
    Syncs payment status with Stripe.
    Marks payments as EXPIRED or PAID based on the session status.
    """

    pending_payments = Payment.objects.filter(status="PENDING")

    for payment in pending_payments:
        try:
            session = stripe.checkout.Session.retrieve(payment.session_id)

            if session.status == "expired":
                payment.status = "EXPIRED"
                payment.save()
                print(f"Payment {payment.id} marked as EXPIRED")
            elif session.status == "complete":
                payment.status = "PAID"
                payment.save()
        except Exception as e:
            print(f"Error checking payment {payment.id} : {e}")

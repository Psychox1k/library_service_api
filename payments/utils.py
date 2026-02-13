import stripe
from django.conf import settings

from rest_framework.exceptions import ValidationError
from .models import Payment


def create_payment_session(borrowing):
    """
    Calculates the total price for the borrowing and creates a Stripe Checkout Session.
    :param borrowing:
    :return:
    """
    try:
        duration = borrowing.expected_return_date - borrowing.borrow_date

        days = max(duration.days, 1)

        total_price = days * borrowing.book.daily_fee

        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": borrowing.book.title,
                        },
                        "unit_amount": int(total_price * 100),
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url='http://localhost:8000/api/payments/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:8000/api/payments/cancel',
        )

        Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=borrowing,
            session_url=session.url,
            session_id=session.id,
            money_to_pay=total_price
        )
        print("\n--- SUCCESS! ---")
        print(f"Session ID:  {session.id}")
        print(f"Session URL: {session.url}")
        print("----------------\n")

    except Exception as e:

        print(f"Error: {e}")


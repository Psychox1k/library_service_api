import os

import stripe

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


def create_stripe_session(borrowing):
    """
    Calculates the total price for the borrowing and creates a Stripe Checkout Session.
    :param borrowing:
    :return:
    """

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

    return session

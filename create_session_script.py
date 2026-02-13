# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
import os
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


def create_session():
    try:
        session = stripe.checkout.Session.create(
          line_items=[
            {
              "price_data": {
                "currency": "usd",
                "product_data": {
                        "name": "Sigma",
                    },
                "unit_amount": 2000,
              },
              "quantity": 1,
            },
          ],
          mode="payment",
            success_url='http://localhost:8000/api/payments/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:8000/api/payments/cancel',
        )

        print("\n--- SUCCESS! ---")
        print(f"Session ID:  {session.id}")
        print(f"Session URL: {session.url}")
        print("----------------\n")

    except Exception as e:

        print(f"Error: {e}")

if __name__ == "__main__":
    create_session()
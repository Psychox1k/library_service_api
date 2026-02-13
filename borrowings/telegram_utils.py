import os
import requests

from dotenv import load_dotenv

load_dotenv()


def send_telegram_message(text):
    """
        Sends a message to the configured Telegram chat.
        Does not raise exceptions to prevent blocking the main app flow.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram token or chat_id is missing.")

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code != 200:
            print(f"Error sending to Telegram: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Telegram connection error {e}")

from celery import shared_task
from django.utils import timezone
from borrowings.models import Borrowing
from borrowings.telegram_utils import send_telegram_message


@shared_task
def check_overdue_borrowings():
    today = timezone.now().date()

    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today,
        actual_return_date__isnull=True
    )
    if not overdue_borrowings.exists():
        send_telegram_message("✅ No borrowings overdue today!")
    else:
        for borrowing in overdue_borrowings:
            text = (
                f"🚨 <b>Overdue Borrowing!</b>\n\n"
                f"📧 <b>User:</b> {borrowing.user.email}\n"
                f"📖 <b>Book:</b> {borrowing.book.title}\n"
                f"📅 <b>Expected:</b> {borrowing.expected_return_date}\n"
                f"🆔 <b>ID:</b> {borrowing.id}"
            )
            send_telegram_message(text)


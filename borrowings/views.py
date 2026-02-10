from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
)
from borrowings.telegram_utils import send_telegram_message


class BorrowingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing borrowing of books.

    Handles Create, Read, Update, and Delete operations for Borrowing model.
    """
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Retrieve the borrowings queryset.

        Filters the queryset so that:
        - Admin users (staff) can see all borrowings.
        - Regular users can only see their own borrowing history.
        """
        user = self.request.user
        if user.is_staff:
            return Borrowing.objects.all()
        return Borrowing.objects.filter(user=user)

    def get_serializer_class(self):
        """
        Return the serializer class based on the action.

        - 'list' and 'retrieve': Returns BorrowingListSerializer (includes detailed book info).
        - Other actions: Returns the standard BorrowingSerializer.
        """
        if self.action in ("list", "retrieve"):
            return BorrowingListSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        """
        Create a new borrowing.

        Automatically assigns the currently authenticated user to the borrowing instance.
        """
        borrowing = serializer.save(user=self.request.user)

        message = (
            f"📚 <b>New Borrowing Created!</b>\n\n"
            f"👤 <b>User:</b> {borrowing.user.email}\n"
            f"📖 <b>Book:</b> {borrowing.book.title}\n"
            f"📅 <b>Expected Return:</b> {borrowing.expected_return_date}\n"
            f"🆔 <b>Borrowing ID:</b> {borrowing.id}"
        )

        send_telegram_message(message)
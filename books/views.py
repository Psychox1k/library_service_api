from django.shortcuts import render
from rest_framework import serializers, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from books.models import Book
from books.permissions import IsAdminOrReadOnly
from books.serializers import BookSerializer


# Create your views here.
class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrReadOnly,)

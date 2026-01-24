from django.shortcuts import render
from rest_framework import serializers, viewsets

from books.models import Book
from books.serializers import BookSerializer


# Create your views here.
class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()

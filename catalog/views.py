import django
from django.shortcuts import render
from .models import Book, BookInstance, Author, Genre


def index(request):
    context = {
        'num_books': Book.objects.count(),
        'num_instances': BookInstance.objects.count(),
        'num_instances_available': BookInstance.objects.filter(status='a').count(),
        'num_authors': Author.objects.count(),
        'num_genres': Genre.objects.count(),
        'recent_books': Book.objects.order_by('-id')[:5],
        'django_version': django.get_version(),
    }
    return render(request, 'catalog/index.html', context)


def book_list(request):
    q = request.GET.get('q', '')
    books = Book.objects.all().order_by('title')
    if q:
        books = books.filter(title__icontains=q) | books.filter(author__last_name__icontains=q)
    return render(request, 'catalog/book_list.html', {'books': books, 'query': q})


def author_list(request):
    authors = Author.objects.all().order_by('last_name')
    return render(request, 'catalog/author_list.html', {'authors': authors})

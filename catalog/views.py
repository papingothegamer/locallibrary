import django
from django.shortcuts import render
from .models import Book, BookInstance, Author, Genre

SPINE_COLORS = [
    '#2E4057', '#E76F51', '#2A9D8F', '#E9C46A', '#9B5DE5',
    '#F72585', '#4361EE', '#F4A261', '#264653', '#A8DADC',
    '#C77DFF', '#06D6A0', '#EF233C', '#FB8500', '#3A86FF',
    '#8338EC', '#FF006E', '#FFBE0B', '#3D405B', '#81B29A',
]

SPINE_HEIGHTS = [
    155, 170, 145, 180, 160, 140, 175, 150, 165, 185,
    148, 172, 158, 142, 168, 178, 153, 163, 147, 182,
]


def index(request):
    books = Book.objects.all().order_by('id')
    shelf_books = []
    for i, book in enumerate(books):
        book.spine_color = SPINE_COLORS[i % len(SPINE_COLORS)]
        book.spine_height = SPINE_HEIGHTS[i % len(SPINE_HEIGHTS)]
        shelf_books.append(book)

    context = {
        'num_books': Book.objects.count(),
        'num_instances': BookInstance.objects.count(),
        'num_instances_available': BookInstance.objects.filter(status='a').count(),
        'num_authors': Author.objects.count(),
        'num_genres': Genre.objects.count(),
        'shelf_books': shelf_books,
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

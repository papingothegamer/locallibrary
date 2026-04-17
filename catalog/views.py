import django
from django.shortcuts import render
from django.http import JsonResponse
from django.views import generic
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

    # --- LECTURE REQUIREMENT: Session Visit Counter ---
    request.session.set_test_cookie()
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        num_visits = request.session.get('num_visits', 0)
        request.session['num_visits'] = num_visits + 1
    else:
        num_visits = -1
    # --------------------------------------------------

    context = {
        'num_books': Book.objects.count(),
        'num_instances': BookInstance.objects.count(),
        'num_instances_available': BookInstance.objects.filter(status='a').count(),
        'num_authors': Author.objects.count(),
        'num_genres': Genre.objects.count(),
        'shelf_books': shelf_books,
        'num_visits': num_visits,
        'django_version': django.get_version(),
    }
    return render(request, 'catalog/index.html', context)

def search_suggestions(request):
    q = request.GET.get('q', '')
    results = []
    if len(q) > 0:
        for a in Author.objects.filter(full_name__icontains=q)[:3]:
            results.append({'text': a.full_name, 'type': 'Author', 'url': a.get_absolute_url()})
        for b in Book.objects.filter(title__icontains=q)[:3]:
            results.append({'text': b.title, 'type': 'Book', 'url': b.get_absolute_url()})
        for g in Genre.objects.filter(name__icontains=q)[:3]:
            results.append({'text': g.name, 'type': 'Genre', 'url': f"/catalog/books/?q={g.name}"})
            
    return JsonResponse({'results': results})

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

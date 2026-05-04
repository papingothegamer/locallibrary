import time
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .models import Book, BookInstance, Author, Genre
from datetime import date, timedelta

SPINE_COLORS = ['#2E4057', '#E76F51', '#2A9D8F', '#E9C46A', '#9B5DE5', '#F72585', '#4361EE', '#F4A261', '#264653', '#A8DADC', '#C77DFF', '#06D6A0', '#EF233C', '#FB8500', '#3A86FF', '#8338EC', '#FF006E', '#FFBE0B', '#3D405B', '#81B29A']
SPINE_HEIGHTS = [155, 170, 145, 180, 160, 140, 175, 150, 165, 185, 148, 172, 158, 142, 168, 178, 153, 163, 147, 182]

def attach_book_colors(books):
    """Utility to attach colors dynamically without altering the database models."""
    for book in books:
        book.spine_color = SPINE_COLORS[(book.id or 0) % len(SPINE_COLORS)]
        book.spine_height = SPINE_HEIGHTS[(book.id or 0) % len(SPINE_HEIGHTS)]
    return books

def index(request):
    shelf_books = list(Book.objects.all().order_by('id'))
    attach_book_colors(shelf_books)

    request.session.set_test_cookie()
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        
        # --- Intelligent Visit Counter Logic ---
        num_visits = request.session.get('num_visits', 0)
        last_visit_time = request.session.get('last_visit_time', 0)
        current_time = time.time()
        
        # Only count as a new visit if it's been more than 1 hour (3600 seconds)
        if current_time - last_visit_time > 3600:
            num_visits += 1
            request.session['num_visits'] = num_visits
            request.session['last_visit_time'] = current_time
    else:
        num_visits = -1

    context = {
        'num_books': Book.objects.count(),
        'num_instances': BookInstance.objects.count(),
        'num_instances_available': BookInstance.objects.filter(status='a').count(),
        'num_authors': Author.objects.count(),
        'num_genres': Genre.objects.count(),
        'shelf_books': shelf_books,
        'num_visits': num_visits,
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

@login_required
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    available_copy = book.bookinstance_set.filter(status='a').first()
    if available_copy and request.method == 'POST':
        available_copy.borrower = request.user
        available_copy.status = 'o'
        available_copy.due_back = date.today() + timedelta(days=14)
        available_copy.save()
    return redirect('my-borrowed')

@login_required
def return_book(request, pk):
    copy = get_object_or_404(BookInstance, pk=pk)
    if copy.borrower == request.user and request.method == 'POST':
        copy.borrower = None
        copy.status = 'a'
        copy.due_back = None
        copy.save()
    return redirect('my-borrowed')

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attach_book_colors(context['book_list'])
        return context

class BookDetailView(generic.DetailView):
    model = Book
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_copies'] = self.object.bookinstance_set.filter(status='a').count()
        
        sim_books = list(Book.objects.filter(genre__in=self.object.genre.all()).exclude(pk=self.object.pk).distinct()[:3])
        context['similar_books'] = attach_book_colors(sim_books)
        attach_book_colors([self.object])
        return context

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['similar_authors'] = Author.objects.exclude(pk=self.object.pk).order_by('?')[:3]
        context['author_books'] = attach_book_colors(list(self.object.book_set.all()))
        return context

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for inst in context['bookinstance_list']:
            if inst.book: attach_book_colors([inst.book])
        return context

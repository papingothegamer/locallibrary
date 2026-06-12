"""
============================================================
VIEWS — catalog/views.py
============================================================
Contains all view functions and class-based views for the
catalog app. Each view processes an HTTP request and returns
a response (usually by rendering an HTML template).

View → URL → Template mapping:
  index()                  → /catalog/           → catalog/index.html
  search_suggestions()     → /catalog/search-suggestions/ → JSON response
  borrow_book()            → /catalog/book/<pk>/borrow/   → redirect
  return_book()            → /catalog/bookinstance/<uuid>/return/ → redirect
  renew_book_librarian()   → /catalog/book/<uuid>/renew/  → catalog/book_renew_librarian.html
  SignUpView               → /catalog/signup/     → registration/signup.html
  BookListView             → /catalog/books/      → catalog/book_list.html
  BookDetailView           → /catalog/book/<pk>   → catalog/book_detail.html
  AuthorListView           → /catalog/authors/    → catalog/author_list.html
  AuthorDetailView         → /catalog/author/<pk> → catalog/author_detail.html
  LoanedBooksByUserListView   → /catalog/mybooks/   → catalog/bookinstance_list_borrowed_user.html
  LoanedBooksByAllListView    → /catalog/borrowed/  → catalog/bookinstance_list_borrowed_by_all.html
  AuthorCreate/Update/Delete  → /catalog/author/create|update|delete/
  BookCreate/Update/Delete    → /catalog/book/create|update|delete/
============================================================
"""

import time
import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from .models import Book, BookInstance, Author, Genre
from .forms import RenewBookModelForm

# ============================================================
# SPINE COLOR/HEIGHT ARRAYS
# ============================================================
# These are used by attach_book_colors() to assign deterministic
# visual properties to books based on their ID. In the main
# branch, these colors and heights style the interactive bookshelf.
# In the minimal-style branch, the values are still attached to
# book objects but are NOT referenced in the simplified templates.
# ============================================================
SPINE_COLORS = ['#2E4057', '#E76F51', '#2A9D8F', '#E9C46A', '#9B5DE5', '#F72585', '#4361EE', '#F4A261', '#264653', '#A8DADC', '#C77DFF', '#06D6A0', '#EF233C', '#FB8500', '#3A86FF', '#8338EC', '#FF006E', '#FFBE0B', '#3D405B', '#81B29A']
SPINE_HEIGHTS = [155, 170, 145, 180, 160, 140, 175, 150, 165, 185, 148, 172, 158, 142, 168, 178, 153, 163, 147, 182]


def attach_book_colors(books):
    """
    Attaches spine_color and spine_height attributes to each book
    in the queryset/list. Used by the main branch's bookshelf UI.
    These attributes are unused in the minimal-style templates but
    are kept for compatibility.

    Args:
        books: A list or queryset of Book objects

    Returns:
        The same list with .spine_color and .spine_height set on each book
    """
    for book in books:
        book.spine_color = SPINE_COLORS[(book.id or 0) % len(SPINE_COLORS)]
        book.spine_height = SPINE_HEIGHTS[(book.id or 0) % len(SPINE_HEIGHTS)]
    return books


# ============================================================
# HOMEPAGE VIEW
# ============================================================
def index(request):
    """
    HOME PAGE — Renders the library homepage (catalog/index.html).

    URL: /catalog/ (name='index')
    Template: catalog/index.html

    Displays on the frontend:
      - Library statistics (book count, copy count, author count, etc.)
      - A search bar with autocomplete
      - A list of all books (shown as a simple list in minimal version)
      - A visit counter tracked via session cookies

    Context variables passed to the template:
      - num_books:              Total number of Book objects
      - num_instances:          Total number of BookInstance objects (copies)
      - num_instances_available: Number of available copies (status='a')
      - num_authors:            Total number of Author objects
      - num_genres:             Total number of Genre objects
      - shelf_books:            All books ordered by ID (for the book list)
      - num_visits:             Session-tracked visit count (increments hourly)
    """
    # Fetch all books for the homepage list
    shelf_books = list(Book.objects.all().order_by('id'))
    attach_book_colors(shelf_books)  # Attaches colors (unused in minimal templates)

    # --- SESSION-BASED VISIT COUNTER ---
    # Uses Django's session framework to track how many times
    # this user has visited. Increments at most once per hour
    # to avoid inflating the count on page refreshes.
    request.session.set_test_cookie()
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        num_visits = request.session.get('num_visits', 0)
        last_visit_time = request.session.get('last_visit_time', 0)
        current_time = time.time()
        # Only increment if more than 1 hour (3600 seconds) has passed
        if current_time - last_visit_time > 3600:
            num_visits += 1
            request.session['num_visits'] = num_visits
            request.session['last_visit_time'] = current_time
    else:
        # Cookies not working — set visits to -1 (template hides the counter)
        num_visits = -1

    # Build the context dictionary — each key becomes a template variable
    context = {
        'num_books': Book.objects.count(),                                    # Displayed in stats table
        'num_instances': BookInstance.objects.count(),                        # Displayed in stats table
        'num_instances_available': BookInstance.objects.filter(status='a').count(),  # Displayed in stats table
        'num_authors': Author.objects.count(),                               # Displayed in stats table
        'num_genres': Genre.objects.count(),                                  # Displayed in stats table
        'shelf_books': shelf_books,                                          # Displayed as book list on homepage
        'num_visits': num_visits,                                            # Displayed in stats table
    }
    return render(request, 'catalog/index.html', context)


# ============================================================
# SEARCH SUGGESTIONS API
# ============================================================
def search_suggestions(request):
    """
    SEARCH AUTOCOMPLETE API — Returns JSON search suggestions.

    URL: /catalog/search-suggestions/?q=<query> (name='search-suggestions')
    Response: JSON — { "results": [ {"text": ..., "type": ..., "url": ...}, ... ] }

    This is called by the JavaScript in index.html when the user
    types in the search bar. It queries Authors, Books, and Genres
    whose names contain the search query (case-insensitive) and
    returns up to 3 results of each type.

    Displayed on the frontend:
      - As dropdown suggestions below the search input on the homepage
      - Each suggestion is a clickable link to the relevant detail page
    """
    q = request.GET.get('q', '')
    results = []
    if len(q) > 0:
        # Search authors by full_name — results link to author detail page
        for a in Author.objects.filter(full_name__icontains=q)[:3]:
            results.append({'text': a.full_name, 'type': 'Author', 'url': a.get_absolute_url()})
        # Search books by title — results link to book detail page
        for b in Book.objects.filter(title__icontains=q)[:3]:
            results.append({'text': b.title, 'type': 'Book', 'url': b.get_absolute_url()})
        # Search genres by name — results link to filtered book list
        for g in Genre.objects.filter(name__icontains=q)[:3]:
            results.append({'text': g.name, 'type': 'Genre', 'url': f"/catalog/books/?q={g.name}"})
    return JsonResponse({'results': results})


# ============================================================
# BORROW BOOK VIEW
# ============================================================
@login_required  # Redirects to login page if user is not authenticated
def borrow_book(request, pk):
    """
    BORROW BOOK — Assigns an available copy to the logged-in user.

    URL: /catalog/book/<pk>/borrow/ (name='borrow-book')
    Method: POST only (form on book_detail.html)
    Redirect: /catalog/mybooks/ (my-borrowed)

    Displayed on the frontend:
      - The "Borrow a Copy" button on the book detail page triggers this
      - After borrowing, the user is redirected to their "My Borrowed" page
      - The borrowed copy appears in their list with a 14-day due date

    Logic:
      1. Finds the first BookInstance with status='a' (available) for this book
      2. Sets borrower to current user, status to 'o' (on loan)
      3. Sets due_back to 14 days from today
    """
    book = get_object_or_404(Book, pk=pk)
    available_copy = book.bookinstance_set.filter(status='a').first()
    if available_copy and request.method == 'POST':
        available_copy.borrower = request.user
        available_copy.status = 'o'
        available_copy.due_back = datetime.date.today() + datetime.timedelta(days=14)
        available_copy.save()
    return redirect('my-borrowed')


# ============================================================
# RETURN BOOK VIEW
# ============================================================
@login_required
def return_book(request, pk):
    """
    RETURN BOOK — Marks a borrowed copy as available again.

    URL: /catalog/bookinstance/<uuid>/return/ (name='return-book')
    Method: POST only (form on bookinstance_list_borrowed_user.html)
    Redirect: /catalog/mybooks/ (my-borrowed)

    Displayed on the frontend:
      - The "Return" button on the "My Borrowed" page triggers this
      - After returning, the book disappears from the user's borrowed list

    Security:
      - Only the actual borrower can return the book (checked via copy.borrower == request.user)
    """
    copy = get_object_or_404(BookInstance, pk=pk)
    if copy.borrower == request.user and request.method == 'POST':
        copy.borrower = None
        copy.status = 'a'  # Set back to 'available'
        copy.due_back = None
        copy.save()
    return redirect('my-borrowed')


# ============================================================
# RENEW BOOK (LIBRARIAN ONLY)
# ============================================================
@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """
    RENEW BOOK — Allows a librarian to extend a book's due date.

    URL: /catalog/book/<uuid>/renew/ (name='renew-book-librarian')
    Template: catalog/book_renew_librarian.html
    Permission: catalog.can_mark_returned (librarian only)

    Displayed on the frontend:
      - Accessed via the "Renew" link on the Librarian Desk page
      - Shows a form with a date picker pre-filled to 3 weeks from today
      - On valid submission, updates the due_back date and redirects
        back to the Librarian Desk

    Uses RenewBookModelForm (forms.py) which validates:
      - Date is not in the past
      - Date is not more than 4 weeks ahead
    """
    book_instance = get_object_or_404(BookInstance, pk=pk)
    if request.method == 'POST':
        form = RenewBookModelForm(request.POST)
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()
            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        # Pre-fill the form with a date 3 weeks from today
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {'form': form, 'book_instance': book_instance}
    return render(request, 'catalog/book_renew_librarian.html', context)


# ============================================================
# SIGNUP VIEW
# ============================================================
class SignUpView(generic.CreateView):
    """
    USER REGISTRATION — Displays and processes the signup form.

    URL: /catalog/signup/ (name='signup')
    Template: registration/signup.html
    Form: Django's built-in UserCreationForm (username + password)

    Displayed on the frontend:
      - The "Sign Up" link in the navigation bar leads here
      - Shows username and password fields
      - On success, redirects to the login page
    """
    form_class = UserCreationForm
    success_url = reverse_lazy('login')  # Redirect to login after signup
    template_name = 'registration/signup.html'


from .forms import LibrarianSignUpForm

class LibrarianSignUpView(generic.CreateView):
    """
    LIBRARIAN REGISTRATION — Displays and processes the librarian signup form.

    URL: /catalog/librarian-signup/ (name='librarian-signup')
    Template: registration/librarian_signup.html
    Form: LibrarianSignUpForm (UserCreationForm + Secret Code)

    Displayed on the frontend:
      - Shows username, password, and secret code fields
      - On success, redirects to the login page
    """
    form_class = LibrarianSignUpForm
    success_url = reverse_lazy('login')  # Redirect to login after signup
    template_name = 'registration/librarian_signup.html'


# ============================================================
# BOOK LIST VIEW
# ============================================================
class BookListView(generic.ListView):
    """
    BOOK LIST — Displays a paginated list of all books.

    URL: /catalog/books/ (name='books')
    Template: catalog/book_list.html (default for Book model)
    Context variable: book_list (queryset of all Book objects)

    Displayed on the frontend:
      - Shows all books with titles, authors, and genres
      - Paginated: 10 books per page with Previous/Next links
    """
    model = Book
    paginate_by = 10  # Show 10 books per page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Attach spine colors to books (unused in minimal templates)
        attach_book_colors(context['book_list'])
        return context


# ============================================================
# BOOK DETAIL VIEW
# ============================================================
class BookDetailView(generic.DetailView):
    """
    BOOK DETAIL — Displays full information for a single book.

    URL: /catalog/book/<pk> (name='book-detail')
    Template: catalog/book_detail.html (default for Book model)
    Context variable: book (single Book object)

    Displayed on the frontend:
      - Book title, author (linked), synopsis, metadata (ISBN, language, genres)
      - Borrow button (if copies available and user is authenticated)
      - Similar books section (up to 3 books sharing genres)
      - Edit/Delete buttons (if user is a librarian)
    """
    model = Book

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Count available copies — displayed as "X copy/copies available" on the page
        context['available_copies'] = self.object.bookinstance_set.filter(status='a').count()
        # Find similar books (same genre, different book) — displayed in "Similar Books" section
        sim_books = list(Book.objects.filter(genre__in=self.object.genre.all()).exclude(pk=self.object.pk).distinct()[:3])
        context['similar_books'] = attach_book_colors(sim_books)
        attach_book_colors([self.object])
        return context


# ============================================================
# AUTHOR LIST VIEW
# ============================================================
class AuthorListView(generic.ListView):
    """
    AUTHOR LIST — Displays a paginated list of all authors.

    URL: /catalog/authors/ (name='authors')
    Template: catalog/author_list.html (default for Author model)
    Context variable: author_list (queryset of all Author objects)

    Displayed on the frontend:
      - Shows all authors with names, lifespan, and book count
      - Paginated: 10 authors per page
    """
    model = Author
    paginate_by = 10


# ============================================================
# AUTHOR DETAIL VIEW
# ============================================================
class AuthorDetailView(generic.DetailView):
    """
    AUTHOR DETAIL — Displays full information for a single author.

    URL: /catalog/author/<pk> (name='author-detail')
    Template: catalog/author_detail.html (default for Author model)
    Context variable: author (single Author object)

    Displayed on the frontend:
      - Author name, lifespan, biography
      - List of published works (books by this author)
      - "Discover Other Authors" section (3 random other authors)
      - Edit/Delete buttons (if user is a librarian)
    """
    model = Author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get 3 random other authors for the "Discover" section
        context['similar_authors'] = Author.objects.exclude(pk=self.object.pk).order_by('?')[:3]
        # Get all books by this author — displayed in "Published Works" section
        context['author_books'] = attach_book_colors(list(self.object.book_set.all()))
        return context


# ============================================================
# MY BORROWED BOOKS VIEW (Authenticated Users)
# ============================================================
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """
    MY BORROWED BOOKS — Shows books borrowed by the current user.

    URL: /catalog/mybooks/ (name='my-borrowed')
    Template: catalog/bookinstance_list_borrowed_user.html
    Access: Login required (redirects to login if not authenticated)

    Displayed on the frontend:
      - List of BookInstances where borrower = current user and status = 'o'
      - Each item shows: book title, due date (color-coded), return button
      - Empty state message if no books are borrowed
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        """Filters to only show books borrowed by the currently logged-in user."""
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Attach colors to each borrowed book (unused in minimal templates)
        for inst in context['bookinstance_list']:
            if inst.book:
                attach_book_colors([inst.book])
        return context


# ============================================================
# LIBRARIAN DESK VIEW (Librarian Permission Required)
# ============================================================
class LoanedBooksByAllListView(PermissionRequiredMixin, generic.ListView):
    """
    LIBRARIAN DESK — Shows ALL borrowed books across all users.

    URL: /catalog/borrowed/ (name='all-borrowed')
    Template: catalog/bookinstance_list_borrowed_by_all.html
    Access: Requires 'catalog.can_mark_returned' permission

    Displayed on the frontend:
      - List of ALL BookInstances with status='o' (on loan)
      - Each item shows: book title, borrower username, due date, renew link
      - Renew link leads to the renew_book_librarian form
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_by_all.html'
    permission_required = 'catalog.can_mark_returned'
    paginate_by = 10

    def get_queryset(self):
        """Returns all on-loan BookInstances, ordered by due date."""
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for inst in context['bookinstance_list']:
            if inst.book:
                attach_book_colors([inst.book])
        return context


# ============================================================
# LIBRARIAN CRUD VIEWS — Generic Editing Views
# ============================================================
# These views use Django's generic CreateView, UpdateView, and
# DeleteView to handle form rendering and database operations.
# All require specific permissions (librarian-only access).
# Each uses a default template name based on the model name:
#   - CreateView/UpdateView → <model>_form.html
#   - DeleteView → <model>_confirm_delete.html
# ============================================================

class AuthorCreate(PermissionRequiredMixin, CreateView):
    """
    CREATE AUTHOR — Form to add a new author.
    URL: /catalog/author/create/ (name='author-create')
    Template: catalog/author_form.html
    Redirects to: The new author's detail page (via get_absolute_url)
    """
    model = Author
    fields = ['full_name', 'date_of_birth', 'date_of_death', 'bio']
    permission_required = 'catalog.add_author'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    """
    UPDATE AUTHOR — Form to edit an existing author.
    URL: /catalog/author/<pk>/update/ (name='author-update')
    Template: catalog/author_form.html (same template as create)
    Redirects to: The updated author's detail page
    """
    model = Author
    fields = ['full_name', 'date_of_birth', 'date_of_death', 'bio']
    permission_required = 'catalog.change_author'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    """
    DELETE AUTHOR — Confirmation page to delete an author.
    URL: /catalog/author/<pk>/delete/ (name='author-delete')
    Template: catalog/author_confirm_delete.html
    Redirects to: Author list page (/catalog/authors/)
    """
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'


class BookCreate(PermissionRequiredMixin, CreateView):
    """
    CREATE BOOK — Form to add a new book.
    URL: /catalog/book/create/ (name='book-create')
    Template: catalog/book_form.html
    Redirects to: The new book's detail page (via get_absolute_url)
    """
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.add_book'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    """
    UPDATE BOOK — Form to edit an existing book.
    URL: /catalog/book/<pk>/update/ (name='book-update')
    Template: catalog/book_form.html (same template as create)
    Redirects to: The updated book's detail page
    """
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.change_book'


class BookDelete(PermissionRequiredMixin, DeleteView):
    """
    DELETE BOOK — Confirmation page to delete a book.
    URL: /catalog/book/<pk>/delete/ (name='book-delete')
    Template: catalog/book_confirm_delete.html
    Redirects to: Book list page (/catalog/books/)
    """
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.delete_book'

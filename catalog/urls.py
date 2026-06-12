"""
============================================================
URL CONFIGURATION — catalog/urls.py
============================================================
Maps URL patterns to views for the catalog app.
This file is included by the project-level urls.py via:
    path('catalog/', include('catalog.urls'))

So all URLs here are prefixed with /catalog/.
============================================================
"""

from django.urls import path
from . import views

urlpatterns = [
    # --- PUBLIC PAGES ---

    # HOMEPAGE: Displays library stats, search bar, and book list
    # View: views.index (function-based view)
    # Template: catalog/index.html
    path('', views.index, name='index'),

    # BOOK LIST: Paginated list of all books in the library
    # View: views.BookListView (class-based ListView)
    # Template: catalog/book_list.html
    path('books/', views.BookListView.as_view(), name='books'),

    # BOOK DETAIL: Full details for a single book (by primary key)
    # View: views.BookDetailView (class-based DetailView)
    # Template: catalog/book_detail.html
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),

    # AUTHOR LIST: Paginated list of all authors
    # View: views.AuthorListView (class-based ListView)
    # Template: catalog/author_list.html
    path('authors/', views.AuthorListView.as_view(), name='authors'),

    # AUTHOR DETAIL: Full details for a single author (by primary key)
    # View: views.AuthorDetailView (class-based DetailView)
    # Template: catalog/author_detail.html
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),

    # SEARCH SUGGESTIONS API: Returns JSON autocomplete results
    # View: views.search_suggestions (function-based view)
    # Response: JSON (no template — consumed by JavaScript on the homepage)
    path('search-suggestions/', views.search_suggestions, name='search-suggestions'),

    # SIGNUP: User registration page
    # View: views.SignUpView (class-based CreateView)
    # Template: registration/signup.html
    path('signup/', views.SignUpView.as_view(), name='signup'),

    # LIBRARIAN SIGNUP: Librarian registration page
    # View: views.LibrarianSignUpView (class-based CreateView)
    # Template: registration/librarian_signup.html
    path('librarian-signup/', views.LibrarianSignUpView.as_view(), name='librarian-signup'),

    # --- AUTHENTICATED USER ACTIONS ---

    # BORROW BOOK: Assigns an available copy to the logged-in user (POST only)
    # View: views.borrow_book (function-based, @login_required)
    # Redirect: /catalog/mybooks/ (no template — just processes and redirects)
    path('book/<int:pk>/borrow/', views.borrow_book, name='borrow-book'),

    # RETURN BOOK: Marks a borrowed copy as available (POST only)
    # View: views.return_book (function-based, @login_required)
    # Redirect: /catalog/mybooks/ (no template — just processes and redirects)
    path('bookinstance/<uuid:pk>/return/', views.return_book, name='return-book'),

    # MY BORROWED BOOKS: List of books borrowed by the current user
    # View: views.LoanedBooksByUserListView (class-based, LoginRequiredMixin)
    # Template: catalog/bookinstance_list_borrowed_user.html
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),

    # --- LIBRARIAN-ONLY PAGES (require 'catalog.can_mark_returned' permission) ---

    # ALL BORROWED BOOKS: Librarian desk showing all active loans
    # View: views.LoanedBooksByAllListView (class-based, PermissionRequiredMixin)
    # Template: catalog/bookinstance_list_borrowed_by_all.html
    path('borrowed/', views.LoanedBooksByAllListView.as_view(), name='all-borrowed'),

    # RENEW BOOK: Librarian form to extend a book's due date
    # View: views.renew_book_librarian (function-based, @permission_required)
    # Template: catalog/book_renew_librarian.html
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),

    # --- LIBRARIAN CRUD — Author Management ---

    # CREATE AUTHOR: Form to add a new author (requires 'catalog.add_author')
    # View: views.AuthorCreate (CreateView)
    # Template: catalog/author_form.html
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),

    # UPDATE AUTHOR: Form to edit an existing author (requires 'catalog.change_author')
    # View: views.AuthorUpdate (UpdateView)
    # Template: catalog/author_form.html (same as create)
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),

    # DELETE AUTHOR: Confirmation page to delete an author (requires 'catalog.delete_author')
    # View: views.AuthorDelete (DeleteView)
    # Template: catalog/author_confirm_delete.html
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),

    # --- LIBRARIAN CRUD — Book Management ---

    # CREATE BOOK: Form to add a new book (requires 'catalog.add_book')
    # View: views.BookCreate (CreateView)
    # Template: catalog/book_form.html
    path('book/create/', views.BookCreate.as_view(), name='book-create'),

    # UPDATE BOOK: Form to edit an existing book (requires 'catalog.change_book')
    # View: views.BookUpdate (UpdateView)
    # Template: catalog/book_form.html (same as create)
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),

    # DELETE BOOK: Confirmation page to delete a book (requires 'catalog.delete_book')
    # View: views.BookDelete (DeleteView)
    # Template: catalog/book_confirm_delete.html
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
]

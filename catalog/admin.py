"""
============================================================
ADMIN CONFIGURATION — catalog/admin.py
============================================================
Registers catalog models with Django's admin site so they
can be managed via the /admin/ interface. The admin site is
a separate built-in interface (not part of the public-facing
library website) that allows superusers to directly create,
read, update, and delete database records.

Admin URL: /admin/
(Requires superuser login — separate from the catalog login)
============================================================
"""

from django.contrib import admin
from .models import Author, Genre, Book, BookInstance

# GENRE ADMIN: Simple registration — uses default admin interface
# Allows creating/editing genre names at /admin/catalog/genre/
admin.site.register(Genre)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """
    AUTHOR ADMIN
    ============================================================
    Customizes how Author objects appear in the admin list view.
    Admin URL: /admin/catalog/author/

    list_display: Columns shown in the author list table
      - full_name:     The author's name
      - date_of_birth: Birth date column
      - date_of_death: Death date column
    ============================================================
    """
    list_display = ('full_name', 'date_of_birth', 'date_of_death')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    BOOK ADMIN
    ============================================================
    Customizes how Book objects appear in the admin list view.
    Admin URL: /admin/catalog/book/

    list_display: Columns shown in the book list table
      - title:         The book's title
      - author:        The associated Author (ForeignKey)
      - display_genre: Comma-separated genre names (model method)
    ============================================================
    """
    list_display = ('title', 'author', 'display_genre')


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    """
    BOOKINSTANCE ADMIN
    ============================================================
    Customizes how BookInstance objects appear in the admin.
    Admin URL: /admin/catalog/bookinstance/

    list_display: Columns shown in the instance list table
      - book:     Which book this is a copy of
      - status:   Current loan status (m/o/a/r)
      - borrower: Which user has borrowed it (if any)
      - due_back: When the book is due to be returned
      - id:       UUID of this specific copy

    list_filter: Sidebar filters for quick filtering
      - status:   Filter by loan status
      - due_back: Filter by due date

    fieldsets: Groups fields into sections on the detail/edit form
      - Main section: book, imprint, id
      - Availability: status, due_back, borrower
    ============================================================
    """
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')
    fieldsets = (
        (None, {'fields': ('book', 'imprint', 'id')}),
        ('Availability', {'fields': ('status', 'due_back', 'borrower')}),
    )

"""
============================================================
MODELS — catalog/models.py
============================================================
Defines the database schema for the LocalLibrary application.
Django converts these model classes into database tables.
Each model maps to a template/page on the frontend:

  Genre         → Displayed as tags on book detail & list pages
  Author        → Has its own list page (/catalog/authors/) and
                  detail page (/catalog/author/<pk>)
  Book          → Has its own list page (/catalog/books/) and
                  detail page (/catalog/book/<pk>), also shown
                  on the homepage
  BookInstance  → Represents physical copies; shown on the
                  "My Borrowed" and "Librarian Desk" pages
============================================================
"""

from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date


class Genre(models.Model):
    """
    GENRE MODEL
    ============================================================
    Stores book genres (e.g., "Science Fiction", "Fantasy").
    Frontend display:
      - Shown as genre tags on book detail pages
      - Listed in book list items via Book.display_genre()
      - Searchable via the search-suggestions API endpoint
    Database table: catalog_genre
    ============================================================
    """
    # The genre name, e.g. "Science Fiction" — displayed on book detail/list pages
    name = models.CharField(max_length=200, help_text="Enter a book genre")

    def __str__(self):
        return self.name


class Author(models.Model):
    """
    AUTHOR MODEL
    ============================================================
    Stores author information. Each author can have many books
    (via Book.author ForeignKey).
    Frontend display:
      - Author list page: /catalog/authors/ (author_list.html)
        Shows full_name, lifespan, and book count
      - Author detail page: /catalog/author/<pk> (author_detail.html)
        Shows biography, published works, and similar authors
      - Book detail page: Author name links to author detail
      - Homepage: Author names shown in book list
    Database table: catalog_author
    ============================================================
    """
    # Author's full name in "Last, First" format — displayed as the primary identifier everywhere
    full_name = models.CharField(max_length=200, null=True)

    # Author's biography text — displayed on the author detail page
    bio = models.TextField(max_length=2000, null=True, blank=True, help_text="Enter a brief biography")

    # Birth date — displayed as year on author list/detail pages
    date_of_birth = models.DateField(null=True, blank=True)

    # Death date — displayed as year on author list/detail pages (shows "Present" if null)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        # Default ordering: alphabetical by full_name (affects author list page)
        ordering = ['full_name']

    def get_absolute_url(self):
        """Returns the URL for this author's detail page (author_detail.html)."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return self.full_name or "Unknown"


class Book(models.Model):
    """
    BOOK MODEL
    ============================================================
    Stores book information. The core entity of the library.
    Frontend display:
      - Homepage: Listed in the "All Books" section
      - Book list page: /catalog/books/ (book_list.html)
        Shows title, author, and genres
      - Book detail page: /catalog/book/<pk> (book_detail.html)
        Shows full details, borrow button, similar books
      - Author detail page: Listed under "Published Works"
    Database table: catalog_book
    ============================================================
    """
    # Book title — displayed as the primary text on all book listings and detail page heading
    title = models.CharField(max_length=200)

    # Foreign key to Author — displayed as a link on book detail page
    # SET_NULL: if author is deleted, book remains but author shows as null
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)

    # Book description/summary — displayed under "Synopsis" on book detail page
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")

    # International Standard Book Number — displayed under "Metadata" on book detail page
    isbn = models.CharField('ISBN', max_length=13, unique=True)

    # Many-to-many relationship with Genre — displayed as genre tags on book pages
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")

    # Language the book is written in — displayed under "Metadata" on book detail page
    language = models.CharField(max_length=200, null=True)

    # ---- Visual properties (used in the main branch's fancy UI, unused in minimal) ----

    def get_spine_color(self):
        """
        Returns a deterministic color hex code based on book ID.
        Used in the main branch to color book spines on the shelf.
        Not referenced in the minimal-style templates.
        """
        colors = ['#2E4057', '#E76F51', '#2A9D8F', '#E9C46A', '#9B5DE5', '#F72585', '#4361EE', '#F4A261', '#264653', '#A8DADC', '#C77DFF', '#06D6A0', '#EF233C', '#FB8500', '#3A86FF', '#8338EC', '#FF006E', '#FFBE0B', '#3D405B', '#81B29A']
        return colors[(self.id or 0) % len(colors)]

    def get_spine_height(self):
        """
        Returns a deterministic pixel height based on book ID.
        Used in the main branch for varied book spine heights.
        Not referenced in the minimal-style templates.
        """
        heights = [155, 170, 145, 180, 160, 140, 175, 150, 165, 185, 148, 172, 158, 142, 168, 178, 153, 163, 147, 182]
        return heights[(self.id or 0) % len(heights)]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Returns the URL for this book's detail page (book_detail.html)."""
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        """
        Returns a comma-separated string of the first 3 genre names.
        Displayed on book list pages and book detail metadata section.
        """
        return ', '.join(genre.name for genre in self.genre.all()[:3])


class BookInstance(models.Model):
    """
    BOOKINSTANCE MODEL
    ============================================================
    Represents a specific physical copy of a book. One Book can
    have many BookInstances (copies).
    Frontend display:
      - "My Borrowed" page: /catalog/mybooks/
        Shows books the current user has on loan, with due dates
        and return buttons
      - "Librarian Desk" page: /catalog/borrowed/
        Shows ALL loans across all users, with renew links
      - Book detail page: available_copies count displayed
    Database table: catalog_bookinstance
    ============================================================
    """
    # UUID primary key — uniquely identifies each physical copy
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # Which book this is a copy of — links to the Book model
    # RESTRICT: prevents deleting a Book that still has copies
    book = models.ForeignKey(Book, on_delete=models.RESTRICT, null=True)

    # Publisher/edition info — not currently displayed in templates but stored in DB
    imprint = models.CharField(max_length=200)

    # When the book is due to be returned — displayed on borrowed book pages
    # Null when the book is not on loan
    due_back = models.DateField(null=True, blank=True)

    # Which user has borrowed this copy — displayed on librarian desk
    # SET_NULL: if user is deleted, the copy remains but borrower is cleared
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Loan status choices — determines where/how the copy appears in the frontend
    LOAN_STATUS = (
        ('m', 'Maintenance'),  # Not shown to regular users
        ('o', 'On loan'),      # Shown on borrowed books pages
        ('a', 'Available'),    # Counted in available_copies on book detail page
        ('r', 'Reserved'),     # Not currently used in templates
    )
    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m')

    @property
    def is_overdue(self):
        """
        Returns True if the book is past its due date.
        Displayed on borrowed book pages: overdue items are shown
        in red (text-danger CSS class), on-time items in green
        (text-success CSS class).
        """
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    class Meta:
        # Default ordering by due date (earliest first) — affects borrowed book page order
        ordering = ['due_back']
        # Custom permission used to gate librarian-only features in views and templates
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        return f'{self.id} ({self.book.title})'

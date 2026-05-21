from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date

class Genre(models.Model):
    name = models.CharField(max_length=200, help_text="Enter a book genre")
    def __str__(self): return self.name

class Author(models.Model):
    full_name = models.CharField(max_length=200, null=True)
    bio = models.TextField(max_length=2000, null=True, blank=True, help_text="Enter a brief biography")
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta: ordering = ['full_name']
    def get_absolute_url(self): return reverse('author-detail', args=[str(self.id)])
    def __str__(self): return self.full_name or "Unknown"

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN', max_length=13, unique=True)
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    language = models.CharField(max_length=200, null=True)

    # Deterministic visual properties
    def get_spine_color(self):
        colors = ['#2E4057', '#E76F51', '#2A9D8F', '#E9C46A', '#9B5DE5', '#F72585', '#4361EE', '#F4A261', '#264653', '#A8DADC', '#C77DFF', '#06D6A0', '#EF233C', '#FB8500', '#3A86FF', '#8338EC', '#FF006E', '#FFBE0B', '#3D405B', '#81B29A']
        return colors[(self.id or 0) % len(colors)]

    def get_spine_height(self):
        heights = [155, 170, 145, 180, 160, 140, 175, 150, 165, 185, 148, 172, 158, 142, 168, 178, 153, 163, 147, 182]
        return heights[(self.id or 0) % len(heights)]

    def __str__(self): return self.title
    def get_absolute_url(self): return reverse('book-detail', args=[str(self.id)])
    def display_genre(self): return ', '.join(genre.name for genre in self.genre.all()[:3])

class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    book = models.ForeignKey(Book, on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (('m', 'Maintenance'), ('o', 'On loan'), ('a', 'Available'), ('r', 'Reserved'))
    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m')

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back: return True
        return False

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self): return f'{self.id} ({self.book.title})'

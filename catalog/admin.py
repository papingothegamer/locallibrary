from django.contrib import admin
from .models import Genre, Language, Author, Book, BookInstance

admin.site.site_header = "LocalLibrary Admin"
admin.site.site_title = "LocalLibrary"
admin.site.index_title = "Library Management"

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    pass

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'date_of_birth', 'date_of_death')
    search_fields = ('full_name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre', 'language')
    search_fields = ('title', 'author__full_name')
    list_filter = ('genre', 'language')

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back')
    list_filter = ('status',)
    search_fields = ('book__title',)

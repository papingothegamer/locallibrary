from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('book/<int:pk>/borrow/', views.borrow_book, name='borrow-book'),
    path('bookinstance/<uuid:pk>/return/', views.return_book, name='return-book'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    path('search-suggestions/', views.search_suggestions, name='search-suggestions'),
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
]

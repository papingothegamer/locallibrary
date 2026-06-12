"""
============================================================
PROJECT URL CONFIGURATION — locallibrary/urls.py
============================================================
The root URL configuration for the entire Django project.
This is the entry point for ALL URL routing (referenced by
ROOT_URLCONF in settings.py).

Maps top-level URL paths to the appropriate handlers:
  /admin/    → Django admin site
  /catalog/  → Catalog app URLs (catalog/urls.py)
  /          → Redirects to /catalog/
  /accounts/ → Django's built-in auth URLs (login, logout, etc.)
============================================================
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ADMIN SITE: Django's built-in admin interface for managing database records
    # URL: /admin/
    # Requires superuser login (created via: python manage.py createsuperuser)
    path('admin/', admin.site.urls),

    # CATALOG APP: All library catalog URLs (books, authors, borrow, etc.)
    # URL: /catalog/ (includes all patterns from catalog/urls.py)
    # This is where the main application lives
    path('catalog/', include('catalog.urls')),

    # ROOT REDIRECT: Automatically sends visitors from / to /catalog/
    # This means the homepage is effectively /catalog/ (the index view)
    # permanent=True sends a 301 redirect (browsers cache this)
    path('', RedirectView.as_view(url='catalog/', permanent=True)),

    # AUTHENTICATION URLS: Django's built-in auth views
    # URL: /accounts/ (includes login, logout, password reset, etc.)
    # These use templates from the project-level templates/registration/ directory
    # Provides: /accounts/login/, /accounts/logout/, /accounts/password_reset/, etc.
    path('accounts/', include('django.contrib.auth.urls')),

# In development (DEBUG=True), Django serves static files (CSS, JS)
# directly. In production, a web server (Nginx/Apache) handles this.
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

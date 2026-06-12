"""
============================================================
PROJECT SETTINGS — locallibrary/settings.py
============================================================
Django's main configuration file. Controls all aspects of
the application: installed apps, middleware, database,
templates, authentication, and static files.

This file is referenced by manage.py and wsgi.py via the
DJANGO_SETTINGS_MODULE environment variable.
============================================================
"""

import os
from pathlib import Path

# BASE_DIR: The root directory of the project (parent of this settings file's directory)
# Used as a reference point for constructing file paths throughout the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY: Used for cryptographic signing (sessions, CSRF tokens, etc.)
# WARNING: This is an insecure development key — must be changed in production
SECRET_KEY = 'django-insecure-locallibrary-dev-key-change-in-production'

# LIBRARIAN_ACCESS_CODE: The secret code required to sign up as a librarian
LIBRARIAN_ACCESS_CODE = 'LibraryAdmin2026'

# DEBUG: Enables detailed error pages and auto-reload in development
# Must be False in production for security
DEBUG = True

# ALLOWED_HOSTS: Which hostnames Django will serve requests for
# '*' allows all hosts — restrict this in production
ALLOWED_HOSTS = ['*']

# ============================================================
# INSTALLED APPS
# ============================================================
# Lists all Django apps that are active in this project.
# Django uses this to find models, templates, static files, etc.
# ============================================================
INSTALLED_APPS = [
    'django.contrib.admin',         # Admin site at /admin/
    'django.contrib.auth',          # Authentication system (login, signup, permissions)
    'django.contrib.contenttypes',  # Content type framework (required by auth)
    'django.contrib.sessions',      # Session framework (used for visit counter)
    'django.contrib.messages',      # Message framework (flash messages)
    'django.contrib.staticfiles',   # Static file serving (CSS, JS, images)
    'catalog',                      # Our library catalog app (models, views, templates)
]

# ============================================================
# MIDDLEWARE
# ============================================================
# Middleware processes every request/response. Order matters —
# each middleware wraps the next one in the chain.
# ============================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',       # Security headers (HTTPS, HSTS)
    'django.contrib.sessions.middleware.SessionMiddleware', # Enables session support (visit counter)
    'django.middleware.common.CommonMiddleware',           # URL normalization, Content-Length
    'django.middleware.csrf.CsrfViewMiddleware',          # CSRF protection for POST forms
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Associates requests with users
    'django.contrib.messages.middleware.MessageMiddleware', # Flash message support
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Prevents clickjacking attacks
]

# ROOT_URLCONF: Points to the project-level URL configuration file
# This is the entry point for all URL routing
ROOT_URLCONF = 'locallibrary.urls'

# ============================================================
# TEMPLATE CONFIGURATION
# ============================================================
# Tells Django where to find HTML templates and what context
# processors to use (context processors add variables to every
# template automatically).
# ============================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # DIRS: Additional template directories outside of app directories
        # The 'templates/' directory at the project root contains registration templates
        # (login.html, signup.html) that are outside the catalog app
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        # APP_DIRS: Also look in each app's 'templates/' subdirectory
        # This is how Django finds catalog/templates/base_generic.html, etc.
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',    # Adds 'debug' variable
                'django.template.context_processors.request',  # Adds 'request' variable
                'django.contrib.auth.context_processors.auth', # Adds 'user' and 'perms' variables
                'django.contrib.messages.context_processors.messages', # Adds 'messages' variable
            ],
        },
    },
]

# WSGI_APPLICATION: Entry point for WSGI-compatible web servers
WSGI_APPLICATION = 'locallibrary.wsgi.application'

# ============================================================
# DATABASE
# ============================================================
# Uses SQLite — a file-based database stored as db.sqlite3
# in the project root. Good for development, not for production.
# ============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ============================================================
# PASSWORD VALIDATION
# ============================================================
# These validators are run when users create accounts (signup)
# or change passwords. They enforce password strength rules.
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},  # Password can't be too similar to username
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},           # Minimum 8 characters
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},          # Rejects common passwords
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},         # Can't be entirely numeric
]

# ============================================================
# INTERNATIONALIZATION
# ============================================================
LANGUAGE_CODE = 'en-us'  # Default language for the site
TIME_ZONE = 'UTC'        # Default timezone for datetime storage
USE_I18N = True          # Enable Django's internationalization system
USE_TZ = True            # Store datetimes as UTC in the database

# ============================================================
# STATIC FILES (CSS, JavaScript)
# ============================================================
# STATIC_URL: URL prefix for static files — templates use
# {% static 'css/styles.css' %} which resolves to /static/css/styles.css
# Django's staticfiles app finds files in each app's 'static/' directory
# (e.g., catalog/static/css/styles.css)
# ============================================================
STATIC_URL = 'static/'

# Default primary key field type for models
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# AUTHENTICATION SETTINGS
# ============================================================
# LOGIN_REDIRECT_URL: Where to redirect after successful login
# (if no ?next= parameter is provided). Set to '/' which redirects
# to the homepage via the RedirectView in project urls.py
LOGIN_REDIRECT_URL = '/'

# EMAIL_BACKEND: Uses the console backend for development — prints
# password reset emails to the terminal instead of sending them
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

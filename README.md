# LocalLibrary

A Django library management app built for the University of Lodz Application Servers course.

## Setup

```bash
# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Populate with sample data
python populate.py

# Start the server
python manage.py runserver
```

## Access

- Home: http://127.0.0.1:8000/catalog/
- Admin: http://127.0.0.1:8000/admin/

## Models

- `Genre` — book categories
- `Language` — written language
- `Author` — author with birth/death dates
- `Book` — title, author, ISBN, genre, language
- `BookInstance` — physical copy with loan status

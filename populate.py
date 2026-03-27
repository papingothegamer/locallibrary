import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'locallibrary.settings')
django.setup()

from catalog.models import Author, Genre, Language, Book, BookInstance
from django.contrib.auth.models import User
import uuid
from datetime import date, timedelta

print("Clearing existing data...")
BookInstance.objects.all().delete()
Book.objects.all().delete()
Author.objects.all().delete()
Genre.objects.all().delete()
Language.objects.all().delete()

print("Creating genres...")
genres = {}
for name in ['Science Fiction','Fantasy','Classic Literature','Historical Fiction','Mystery','Non-Fiction','Dystopian']:
    genres[name] = Genre.objects.create(name=name)

print("Creating languages...")
languages = {}
for name in ['English','French','Russian','Spanish']:
    languages[name] = Language.objects.create(name=name)

print("Creating authors...")
authors_data = [
    ('George','Orwell','1903-06-25','1950-01-21'),
    ('Frank','Herbert','1920-10-08','1986-02-11'),
    ('J.R.R.','Tolkien','1892-01-03','1973-09-02'),
    ('Isaac','Asimov','1920-01-02','1992-04-06'),
    ('Ursula','Le Guin','1929-10-21','2018-01-22'),
    ('Fyodor','Dostoevsky','1821-11-11','1881-02-09'),
    ('Gabriel','Garcia Marquez','1927-03-06','2014-04-17'),
    ('Aldous','Huxley','1894-07-26','1963-11-22'),
    ('Philip K.','Dick','1928-12-16','1982-03-02'),
    ('Leo','Tolstoy','1828-09-09','1910-11-20'),
]
authors = {}
for first, last, dob, dod in authors_data:
    # FIXED: Replaced first_name and last_name with full_name
    authors[last] = Author.objects.create(full_name=f'{last}, {first}', date_of_birth=dob, date_of_death=dod)

print("Creating books...")
books_data = [
    ('1984','Orwell',['Dystopian','Classic Literature'],'English','9780451524935','A haunting vision of a totalitarian future.'),
    ('Animal Farm','Orwell',['Classic Literature'],'English','9780451526342','A political allegory mirroring Stalinist Russia.'),
    ('Dune','Herbert',['Science Fiction','Fantasy'],'English','9780441013593','An epic tale of politics and ecology on a desert planet.'),
    ('Dune Messiah','Herbert',['Science Fiction'],'English','9780441015221','The second book in the Dune Chronicles.'),
    ('The Lord of the Rings','Tolkien',['Fantasy'],'English','9780618640157','The epic quest to destroy the One Ring.'),
    ('The Hobbit','Tolkien',['Fantasy','Classic Literature'],'English','9780618968633','A hobbit embarks on an unexpected adventure.'),
    ('Foundation','Asimov',['Science Fiction'],'English','9780553293357','A mathematician develops a plan to preserve civilization.'),
    ('I Robot','Asimov',['Science Fiction'],'English','9780553294385','Linked stories about robots and humans.'),
    ('The Left Hand of Darkness','Le Guin',['Science Fiction'],'English','9780441478125','An envoy visits a planet with no fixed gender.'),
    ('The Dispossessed','Le Guin',['Science Fiction'],'English','9780061054815','A physicist travels between two contrasting worlds.'),
    ('Crime and Punishment','Dostoevsky',['Classic Literature'],'Russian','9780486415871','A student commits murder and grapples with guilt.'),
    ('The Brothers Karamazov','Dostoevsky',['Classic Literature'],'Russian','9780374528379','A philosophical novel on faith and morality.'),
    ('One Hundred Years of Solitude','Garcia Marquez',['Classic Literature','Fantasy'],'Spanish','9780060883287','The multi-generational story of the Buendia family.'),
    ('Brave New World','Huxley',['Dystopian','Science Fiction'],'English','9780060850524','A future society built on pleasure and conformity.'),
    ('Do Androids Dream of Electric Sheep','Dick',['Science Fiction'],'English','9780345404473','A bounty hunter pursues rogue androids.'),
    ('The Man in the High Castle','Dick',['Science Fiction','Historical Fiction'],'English','9780679740674','An alternate history where the Axis powers won WW2.'),
    ('War and Peace','Tolstoy',['Classic Literature','Historical Fiction'],'Russian','9781400079988','Russian society during the Napoleonic era.'),
    ('Anna Karenina','Tolstoy',['Classic Literature'],'Russian','9780143035008','A tragic story of love and Russian society.'),
]
books = {}
for title, author_last, genre_names, lang, isbn, summary in books_data:
    book = Book.objects.create(title=title, author=authors[author_last], summary=summary, isbn=isbn, language=languages[lang])
    for g in genre_names:
        book.genre.add(genres[g])
    books[title] = book

print("Creating book instances...")
borrower = User.objects.filter(is_superuser=True).first()
statuses = ['a','a','a','o','m']
for i, (title, book) in enumerate(books.items()):
    for j in range((i % 3) + 2):
        status = statuses[(i + j) % len(statuses)]
        due_back = date.today() + timedelta(days=(j+1)*7) if status == 'o' else None
        
        # FIXED: Splits full_name by the comma to extract the last name for the imprint
        author_last_name = book.author.full_name.split(',')[0]
        
        BookInstance.objects.create(
            id=uuid.uuid4(), book=book,
            imprint=f'{author_last_name} Press, 2023',
            status=status, due_back=due_back,
            borrower=borrower if status == 'o' else None,
        )

print("\nDone!")
print(f"  Genres:    {Genre.objects.count()}")
print(f"  Languages: {Language.objects.count()}")
print(f"  Authors:   {Author.objects.count()}")
print(f"  Books:     {Book.objects.count()}")
print(f"  Copies:    {BookInstance.objects.count()}")

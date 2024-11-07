from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.urls import reverse # Используется для генерации URL-адресов путем изменения шаблонов URL-адресов

# Create your models here.
class Genre(models.Model):
# Модель, представляющая книжный жанр
    name = models.CharField(max_length=200, help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)")

    def __str__(self):
    # Строка для представления объекта модели (на сайте администратора и т.д.)
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN',max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    def display_genre(self):
        """
        Creates a string for the Genre. This is required to display genre in Admin.
        """
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'

    def __str__(self):
    # Строка для представления модельного объекта.
            return self.title

    def get_absolute_url(self):
    # Возвращает URL-адрес для доступа к определенному экземпляру книги.
            return reverse('book-detail', args=[str(self.id)])

import uuid # Требуется для уникальных экземпляров книг

class BookInstance(models.Model):
# Модель, представляющая конкретный экземпляр книги (т.е. ту, которую можно взять напрокат в библиотеке).
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this particular book across whole library")
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    # status = models.CharField(max_length=200, default='доступен')



    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )
# CharField, для представления данных (конкретного выпуска) о книге.
    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text='Book availability')


    class Meta:
        ordering = ["due_back"]


    def __str__(self):
# Строка для представления модельного объекта
        return '%s (%s)' % (self.id,self.book.title)

class Author(models.Model):
# Модель, представляющая автора.
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    def get_absolute_url(self):
# Возвращает URL-адрес для доступа к конкретному экземпляру author.
        return reverse('author-detail', args=[str(self.id)])


    def __str__(self):
# Строка для представления модельного объекта.
        return '%s, %s' % (self.last_name, self.first_name)

class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(max_length=200, unique=True, help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    def get_absolute_url(self): # подумать
        """Returns the url to access a particular language instance."""
        return reverse('language-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name
#подумать
    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='language_name_case_insensitive_unique',
                violation_error_message = "Language already exists (case insensitive match)"
            ),
        ]
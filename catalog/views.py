from django.http import Http404
from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic

def index(request):  # Функция отображения для домашней страницы сайта.
    # Генерация "количеств" некоторых главных объектов
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()  # Доступные книги (статус = 'a')
    num_authors = Author.objects.count()  # Метод 'all()' применён по умолчанию.
    num_genre = Genre.objects.all().count()
    search_word = None
    if request.method == 'POST':
        search_word = request.POST.get('search_word', '').strip()
        # Проверяем, что слово для поиска не пустое
        if search_word:
            # Получаем количество книг, содержащих слово в заголовке (без учета регистра)
            num_books = Book.objects.filter(title__icontains=search_word.lower()).count()


    # Отрисовка HTML-шаблона index.html с данными внутри переменной контекста context
    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available,
                 'num_authors': num_authors, 'num_genre': num_genre, 'search_word': search_word},
    )

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book






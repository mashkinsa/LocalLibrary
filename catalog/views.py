from django.db.models import Sum
from django.http import Http404
from django.shortcuts import render, redirect
from .forms import RenewBookForm
from .models import Book, Author, BookInstance, Genre, Language
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

def index(request):  # Функция отображения для домашней страницы сайта.
    # Генерация "количеств" некоторых главных объектов
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()  # Доступные книги (статус = 'a')
    num_authors = Author.objects.count()  # Метод 'all()' применён по умолчанию.
    # Количество посещений этого просмотра, подсчитанное в переменной сеанса.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    num_genre = Genre.objects.all().count()
    search_word = ''
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
                 'num_authors': num_authors, 'num_genre': num_genre, 'search_word': search_word, 'num_visits': num_visits},
    )

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author

class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bookinst_list'] = self.get_queryset()  # добавляем список книг в контекст
        return context


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    # Общее представление на основе классов со списком всех книг, которые можно взять напрокат.
    # Доступно только пользователям с разрешением can_mark_returned.
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


from django.shortcuts import get_object_or_404, redirect
from django.views import View
from .models import BookInstance


class MarkBookAsReadView(View):
    def post(self, request, pk):
        book_instance = get_object_or_404(BookInstance, pk=pk, borrower=request.user)
        # Получаем или создаем профиль пользователя
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        # Обновляем общее количество страниц прочитанных пользователем
        user_profile.total_pages_read += book_instance.book.pages  # Убедитесь, что book_instance.book.pages возвращает корректное значение
        user_profile.save()  # Сохраняем изменения в профиле
        # Обновляем статус книги
        book_instance.status = 'a'  # Например, помечаем как доступную
        book_instance.borrower = None
        book_instance.save()  # Сохраняем изменения в книге
        return redirect('my-borrowed')  # Перенаправляем на страницу с взятыми книгами


from django.views.generic import ListView
from .models import UserProfile
class RankingListView(ListView):
    model = UserProfile
    template_name = 'catalog/rating.html'
    context_object_name = 'user_profiles'
    def get_queryset(self):
        return UserProfile.objects.order_by('-total_pages_read')


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk, book_inst=None):
    # Функция просмотра для обновления библиотекарем конкретного экземпляра книги.
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_instance,})


class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'12.10.2024',}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre','pages', 'language']
    permission_required = 'catalog.add_book'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.change_book'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.delete_book'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("book-delete", kwargs={"pk": self.object.pk})
            )

@login_required
def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})

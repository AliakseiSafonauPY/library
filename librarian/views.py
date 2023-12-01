import calendar
import re
import json
from datetime import *

from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, TemplateView, DetailView

from .forms import RegisterReaderForm, RegisterBookForm, RegisterAuthorForm, AuthorsPhotosFormSet, CoverPhotosFormSet
from .models import Book, Reader, Author, CoverPhoto, Copy, AuthorPhoto, ActIssuing, ActReturning, Votes, Violation, \
    ViolationPhoto
from .utils import get_header_nav, get_num_copies


def get_discount(count):
    if 2 < count < 5:
        return 0.9
    elif count == 5:
        return 0.85
    else:
        return 1.0


def time_me():
    today = date.today()
    days = calendar.monthrange(today.year, today.month)[1]
    next_month_date = today + timedelta(days=days)
    return [next_month_date, days]


def get_preliminary_amount(reader):
    today = date.today()

    issuing_num = reader.active_act_issuing
    act = ActIssuing.objects.get(num=issuing_num)
    first_cost = act.tentative_cost
    issuing_date = act.issuing_date
    day = today - issuing_date
    if day.days == 0:
        result = first_cost / 30
    elif 30 >= day.days > 0:
        result = first_cost / 30 * day.days
    else:
        cost = day.days - 30
        result = first_cost + (first_cost / 30) * cost
    return result


def act_reverse(request):
    act = ''
    pk = ''
    if request.method == 'POST':
        act = request.POST['process']
        pk = request.POST['reader']

    return HttpResponseRedirect(f"/{act}?reader={pk}")


class MainPage(ListView):
    template_name = 'main.html'
    model = Book
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['copies'] = get_num_copies()
        context["nav"] = get_header_nav()
        return context


class ReaderList(ListView):
    template_name = 'reader_list.html'
    model = Reader
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'process' in self.request.POST:
            context['process'] = self.request.POST['process']
        context["nav"] = get_header_nav()
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)


class ReaderRegistration(CreateView):
    template_name = 'reader_register.html'
    form_class = RegisterReaderForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav"] = get_header_nav()
        return context


class ShowReader(DetailView):
    model = Reader
    template_name = 'reader_info.html'
    context_object_name = 'reader_info'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav"] = get_header_nav()
        return context


class ShowBook(DetailView):
    model = Book
    template_name = 'book_info.html'
    context_object_name = 'book_info'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav"] = get_header_nav()
        context['authors'] = Author.objects.filter(book_id=context['book_info'].pk)
        context['authors_photo'] = AuthorPhoto.objects.filter(book_id=context['book_info'].pk)
        cover = CoverPhoto.objects.filter(book_id=context['book_info'].pk)
        if len(cover) > 1:
            context['cover_photo'] = CoverPhoto.objects.filter(book_id=context['book_info'].pk)
        context['cover_photo_big'] = CoverPhoto.objects.filter(book_id=context['book_info'].pk)[0]
        return context


class RegisterBookView(TemplateView):
    template_name = 'book_register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book_form = RegisterBookForm(self.request.POST or None)
        author_form = RegisterAuthorForm(self.request.POST or None)
        author_photo_form = AuthorsPhotosFormSet(self.request.POST or self.request.FILES or None)
        cover_form = CoverPhotosFormSet(self.request.POST or self.request.FILES or None)
        context['book_form'] = book_form
        context['author_form'] = author_form
        context['author_photo_form'] = author_photo_form
        context['cover_form'] = cover_form
        context["nav"] = get_header_nav()
        return context

    def dispatch(self, request, *args, **kwargs):

        if request.method == 'POST':
            book_form = RegisterBookForm(request.POST)
            author_form = RegisterAuthorForm(request.POST)
            author_photo_form = AuthorsPhotosFormSet(request.POST, request.FILES)
            cover_form = CoverPhotosFormSet(request.POST, request.FILES)
            if (book_form.is_valid()
                    and author_form.is_valid()
                    and author_photo_form.is_valid()
                    and cover_form.is_valid()):
                print(book_form.cleaned_data['rating'])
                book_form.save()
                book = Book.objects.filter(title_ru=book_form.cleaned_data['title_ru'],
                                           price=book_form.cleaned_data['price'],
                                           price_per_day=book_form.cleaned_data['price_per_day'])[0]
                for b in range(int(book_form.cleaned_data['instance'])):
                    num = b + 1
                    copy = Copy(num=num, status=True, book=book, price_per_day=book.price_per_day)
                    copy.save()
                for al in author_photo_form.cleaned_data:
                    if al:
                        AuthorPhoto.objects.create(author_photo=al['author_photo'], book=book)

                st = author_form.cleaned_data['author'].strip()
                if st:
                    ls = st.split(',')
                    for s in ls:
                        s = s.strip()
                        author = Author(author=s, book=book)
                        author.save()

                # cover_counter = 0
                for cl in cover_form.cleaned_data:
                    if cl:
                        CoverPhoto.objects.create(cover_photo=cl['cover_photo'], book=book)
                #         cover_counter += 1
                return HttpResponseRedirect(book.get_absolute_url())

            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)
        return super().dispatch(request, *args, **kwargs)


class Issuance(TemplateView):
    template_name = 'issuance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c = Copy.objects.all()
        context['preview'] = []
        if self.request.COOKIES.get('copy'):
            value = json.loads(self.request.COOKIES.get('copy'))
            for i in value:
                context['preview'].append(c.filter(id=i)[0])

        act = ActIssuing.objects.all()
        if len(act) > 0:
            context["act"] = f"{int(act[len(act) - 1].pk) + 1}"
        else:
            context["act"] = '1'
        context['time'] = str(time_me()[0])
        context['reader'] = Reader.objects.get(id=self.request.GET.get('reader'))
        if context['reader'].active_act_issuing:
            context['books'] = ActIssuing.objects.get(num=context['reader'].active_act_issuing).copies.all()
        context["nav"] = get_header_nav()
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            response = None
            context = self.get_context_data(**kwargs)
            if request.POST.get('register'):
                reader = Reader.objects.get(id=self.request.GET.get('reader'))
                time_now = str(time_me()[0])
                result = [int(request.POST[string]) for string in list(request.POST) if re.match(r'copy_book', string)]
                end_copies = Copy.objects.select_related('book').filter(pk__in=result)
                tentative_cost = sum([float(end_copies[copy].price_per_day) for copy in range(len(end_copies))]) * time_me()[1] * get_discount(len(end_copies))
                act = ActIssuing(num=request.POST['register'],
                                 return_date=time_now,
                                 tentative_cost=tentative_cost,
                                 reader=reader,
                                 issuing_date=date.today())
                act.save()
                for copy in end_copies:
                    copy.status = False
                    copy.save()
                    act.copies.add(copy)
                    act.save()
                reader.active_act_issuing = act.num
                reader.save()

                response = HttpResponseRedirect(act.get_absolute_url())
                response.delete_cookie('copy')

            if request.POST.get('q'):
                context['popup'] = {'list': []}
                books = Book.objects.filter(title_ru=request.POST.get('q'))
                for book in books:
                    copies = Copy.objects.filter(book=book.pk, status=True)
                    author = Author.objects.filter(book=book.pk)[0]
                    context['popup']['list'].append(
                        {'name': book.title_ru, 'copies': copies, 'id': book.pk, 'author': author.author})

            if request.POST.get('select'):
                repeat = None
                limit = False
                key = ''
                value = ''
                c = Copy.objects.select_related('book').all()
                copy_object = c.get(id=request.POST.get('select'))
                copies = copy_object.id
                if request.COOKIES.get('copy'):
                    val = json.loads(self.request.COOKIES.get('copy'))
                    if len(val) < 5:
                        for i in val:
                            if copy_object.book == c.get(pk=i).book:
                                repeat = copy_object.book
                            if repeat:
                                context["repeat"] = repeat
                                break
                            else:
                                if not limit:
                                    key = 'copy'
                                    value = json.loads(request.COOKIES.get('copy'))
                                    value.append(copies)
                                    if len(val) == 4:
                                        limit = True

                else:
                    key = 'copy'
                    value = [copies]

                if not context.get("repeat"):
                    if not context.get('preview'):
                        context['preview'] = [copy_object]
                    else:
                        context['preview'].append(copy_object)
                    context['limit'] = limit
                    response = self.render_to_response(context)
                    response.set_cookie(key=key, value=value)
            if response:
                return response
            else:
                return self.render_to_response(context)
        return super().dispatch(request, *args, **kwargs)


class Returning(TemplateView):
    template_name = 'return.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        act = ActReturning.objects.all()
        if len(act) > 0:
            context["act"] = f"{int(act[len(act) - 1].pk) + 1}"
        else:
            context["act"] = '1'
        context["nav"] = get_header_nav()
        context['reader'] = Reader.objects.get(id=self.request.GET.get('reader'))
        context['tentative_cost'] = round(get_preliminary_amount(context['reader']), 2)
        context['preliminary_date'] = str(date.today())
        if context['reader'].active_act_issuing:
            context['books'] = ActIssuing.objects.get(num=context['reader'].active_act_issuing).copies.all()
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            response = None
            context = self.get_context_data(**kwargs)
            if request.POST.get('register'):
                reader = Reader.objects.get(id=self.request.GET.get('reader'))

                price_per_day = [float(request.POST[string]) for string in list(request.POST) if
                                 re.match(r'price_per_day', string) and request.POST[string]]
                act_issuing = ActIssuing.objects.get(num=context['reader'].active_act_issuing)
                copies = act_issuing.copies.all()
                issuing_date = act_issuing.issuing_date
                time = request.POST.get('time')
                time = time.split('-')
                time = date(int(time[0]), int(time[1]), int(time[2]))
                time = time - issuing_date
                time = time.days
                tentative_cost = sum([float(copies[copy].price_per_day) for copy in range(len(copies))]) * time * get_discount(len(copies))
                fine = sum([float(request.POST[string]) for string in list(request.POST) if
                            re.match(r'fine', string) and request.POST[string]])
                cost = float(tentative_cost) + fine

                if request.POST['cost']:
                    if float(request.POST['cost']) > cost:
                        cost = float(request.POST['cost'])

                act = ActReturning(num=request.POST['register'],
                                   return_date=request.POST.get('time'),
                                   cost=cost,
                                   reader=reader)
                act.save()

                for copy in copies:
                    act.copies.add(copy)
                    act.save()

                boolean = [(request.POST[string]) for string in list(request.POST) if re.match(r'status', string)]

                tre = [{re.findall('(\d+)', string)[0]: request.POST[string]} for string in list(request.POST) if
                       re.match(r'rating', string)]
                ls = [int(list(lst.keys())[0]) for lst in tre]
                books = Book.objects.filter(pk__in=ls)
                for book in range(len(books)):
                    if list(tre[book].values())[0]:
                        v = Votes(book=books[book], vote=int(list(tre[book].values())[0]))
                        v.save()

                violations = {list(x)[0]: x[list(x)[0]] for x in
                              [{re.findall('(\d+)', string)[0]: request.POST[string]} for string in list(request.POST)
                               if re.match(r'violation', string)] if x[list(x)[0]]}

                images = [{re.findall('(\d+)', string)[0]: request.FILES[string]} for string in list(request.FILES)
                          if re.match(r'img', string)]

                image = {list(images[x])[0]: [y[list(y)[0]] for y in images if list(images[x])[0] == list(y)[0]] for x
                         in range(len(images))}

                for cop in range(len(copies)):
                    copies[cop].price_per_day = price_per_day[cop]
                    if boolean[cop] == 'True':
                        copies[cop].status = True
                    elif boolean[cop] == 'False':
                        copies[cop].status = False
                    copies[cop].save()
                    if violations.get(str(copies[cop].pk)):
                        vio = Violation(copy=copies[cop],
                                        text=violations.get(str(copies[cop].pk)),
                                        act_returning=act)
                        vio.save()
                        if image.get(str(copies[cop].pk)):
                            for loky in image.get(str(copies[cop].pk)):
                                vio_ph = ViolationPhoto(photo=loky,
                                                        violation=vio)
                                vio_ph.save()
                response = HttpResponseRedirect(act.get_absolute_url())

            if response:
                return response
            else:
                return self.render_to_response(context)
        return super().dispatch(request, *args, **kwargs)


class ShowActIssuing(DetailView):
    model = ActIssuing
    template_name = 'act_issuing_info.html'
    context_object_name = 'act_issuing_info'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav"] = get_header_nav()
        return context


class ShowActReturning(DetailView):
    model = ActReturning
    template_name = 'act_returning_info.html'
    context_object_name = 'act_returning_info'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav"] = get_header_nav()
        return context

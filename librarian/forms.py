from django import forms

from .models import Reader, Book, Genre, Author, AuthorPhoto, CoverPhoto, Violation


class MainForm(forms.ModelForm):
    pass


class RegisterReaderForm(forms.ModelForm):
    class Meta:
        model = Reader
        fields = ['surname', 'name', 'patronymic', 'passport_id', 'birth', 'email', 'residence']
        widgets = {
            'surname': forms.TextInput(attrs={'class': 'surname bgw'}),
            'name': forms.TextInput(attrs={'class': 'name bgw'}),
            'patronymic': forms.TextInput(attrs={'class': 'patronymic bgw'}),
            'passport_id': forms.TextInput(attrs={'class': 'passport_id bgw'}),
            'birth': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'birth bgw'}),
            'email': forms.EmailInput(attrs={'class': 'email bgw'}),
            'residence': forms.Textarea(attrs={'class': 'residence bgw', 'rows': 7, 'cols': 25})
        }


class RegisterBookForm(forms.ModelForm):
    genre = forms.ModelMultipleChoiceField(queryset=Genre.objects.all(),
                                           widget=forms.CheckboxSelectMultiple(attrs={'class': 'genre'}))

    class Meta:
        model = Book
        fields = ['title_ru', 'title_origin', 'genre', 'price', 'price_per_day', 'instance', 'publishing', 'pages', 'rating']
        widgets = {
            'title_ru': forms.TextInput(attrs={'class': 'title-ru bgw'}),
            'title_origin': forms.TextInput(attrs={'class': 'title-origin bgw'}),
            'price': forms.NumberInput(attrs={'class': 'price bgw'}),
            'price_per_day': forms.NumberInput(attrs={'class': 'price-per-day bgw'}),
            'instance': forms.NumberInput(attrs={'class': 'instance bgw'}),
            'publishing': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'publishing bgw'}),
            'pages': forms.NumberInput(attrs={'class': 'pages bgw'}),
        }


class RegisterAuthorForm(forms.ModelForm):

    class Meta:
        model = Author
        fields = ['author']
        widgets = {
            'author': forms.Textarea(attrs={'class': 'authors bgw', 'rows': 5, 'cols': 25})
        }


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result



class RegisterAuthorPhotoForm(forms.Form):
    author_photo = MultipleFileField(required=False)


class RegisterCoverForm(forms.Form):
    cover_photo = MultipleFileField()


class RegisterViolationPhotoForm(forms.Form):
    photo = MultipleFileField(required=False)


class ViolationForm(forms.ModelForm):
    class Meta:
        model = Violation
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'violation_text bgw', 'rows': 5, 'cols': 25})
        }
    
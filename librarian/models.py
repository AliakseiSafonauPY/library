from django.db import models
from django.urls import reverse
from django.utils import timezone


class Book(models.Model):
    title_ru = models.CharField(max_length=50)
    title_origin = models.CharField(max_length=50, blank=True)
    genre = models.ManyToManyField('Genre')
    price = models.DecimalField(max_digits=15, decimal_places=2)
    instance = models.IntegerField()
    price_per_day = models.DecimalField(max_digits=15, decimal_places=2)
    publishing = models.DateField(blank=True)
    registration = models.DateTimeField(default=timezone.now)
    pages = models.IntegerField(blank=True)
    rating = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    def get_absolute_url(self, **kwargs):
        return reverse('librarian:book_info', args=(str(self.pk), ))

    def __str__(self):
        return self.title_ru


class Reader(models.Model):
    surname = models.CharField(max_length=40)
    name = models.CharField(max_length=40)
    patronymic = models.CharField(max_length=40, blank=True)
    passport_id = models.CharField(max_length=20, blank=True, unique=True)
    birth = models.DateField()
    email = models.EmailField(unique=True)
    residence = models.TextField(blank=True)
    active_act_issuing = models.IntegerField(blank=True, null=True, unique=True)

    def get_absolute_url(self):
        return reverse('librarian:reader_info', args=(str(self.pk),))

    def __str__(self):
        return f"{self.surname} {self.name} {self.patronymic}"


class Genre(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class CoverPhoto(models.Model):
    cover_photo = models.ImageField(upload_to='image')
    book = models.ForeignKey('Book', on_delete=models.CASCADE)


class Author(models.Model):
    author = models.CharField(max_length=50)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)

    def __str__(self):
        return self.author


class AuthorPhoto(models.Model):
    author_photo = models.ImageField(upload_to='image')
    book = models.ForeignKey('Book', on_delete=models.CASCADE)


class ActIssuing(models.Model):
    num = models.IntegerField()
    copies = models.ManyToManyField('Copy')
    issuing_date = models.DateField()
    return_date = models.DateField()
    tentative_cost = models.DecimalField(max_digits=15, decimal_places=2)
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.return_date} {self.tentative_cost}"

    def get_absolute_url(self):
        return reverse('librarian:act_issuing_info', args=(str(self.pk),))


class ActReturning(models.Model):
    num = models.IntegerField()
    copies = models.ManyToManyField('Copy')
    return_date = models.DateField()
    cost = models.DecimalField(max_digits=15, decimal_places=2)
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.return_date} {self.cost}"

    def get_absolute_url(self):
        return reverse('librarian:act_returning_info', args=(str(self.pk),))


class Violation(models.Model):
    copy = models.ForeignKey('Copy', on_delete=models.CASCADE)
    text = models.TextField()
    act_returning = models.ForeignKey(ActReturning, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class ViolationPhoto(models.Model):
    photo = models.ImageField(upload_to='image')
    violation = models.ForeignKey(Violation, on_delete=models.CASCADE)


class Copy(models.Model):
    num = models.IntegerField()
    status = models.BooleanField(default=True)
    price_per_day = models.DecimalField(max_digits=15, decimal_places=2)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.book},  экземпляр - {self.num}"


class Votes(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    vote = models.IntegerField()


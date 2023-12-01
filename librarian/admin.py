from django.contrib import admin

from .models import Book, Reader, Genre, Author, AuthorPhoto, ActIssuing, ActReturning, Violation, \
    ViolationPhoto, Copy, CoverPhoto, Votes

admin.site.register(Book)
admin.site.register(Reader)
admin.site.register(Genre)
admin.site.register(CoverPhoto)
admin.site.register(Author)
admin.site.register(AuthorPhoto)
admin.site.register(ActIssuing)
admin.site.register(ActReturning)
admin.site.register(Violation)
admin.site.register(ViolationPhoto)
admin.site.register(Copy)
admin.site.register(Votes)
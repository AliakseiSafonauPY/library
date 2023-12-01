from .models import Book, Copy


def get_header_nav():
    return [['Регистрация новой книги', 'librarian:reg_book'],
            ['Регистрация нового читателя', 'librarian:reg_reader'],
            ]


def get_num_copies():
    result = {}
    copies = Copy.objects.all()
    books = Book.objects.all()

    for book in books:
        result[book.pk] = 0
        for copy in copies:
            if copy.book_id == book.pk and copy.status:
                result[book.pk] += 1
    return result

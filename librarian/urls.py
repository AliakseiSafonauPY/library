from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import MainPage, ReaderRegistration, RegisterBookView, ShowBook, ShowReader, ReaderList, Issuance, \
    act_reverse, ShowActIssuing, Returning, ShowActReturning

app = 'librarian'

urlpatterns = [
    path('', MainPage.as_view(), name="main"),
    path('act_returning_info/<int:pk>/', ShowActReturning.as_view(), name="act_returning_info"),
    path('act_issuing_info/<int:pk>/', ShowActIssuing.as_view(), name="act_issuing_info"),
    path('register_reader/', ReaderRegistration.as_view(), name="reg_reader"),
    path('reader_info/<int:pk>/', ShowReader.as_view(), name="reader_info"),
    path('register_book/', RegisterBookView.as_view(), name="reg_book"),
    path('book_info/<int:pk>/', ShowBook.as_view(), name="book_info"),
    path('reader_list/', ReaderList.as_view(), name="reader_list"),
    path('issuance/', Issuance.as_view(), name="issuance"),
    path('return/', Returning.as_view(), name="return"),
    path('act_reverse/', act_reverse, name="act_reverse"),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

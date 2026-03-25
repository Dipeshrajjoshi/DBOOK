# Import necessary classes
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Publisher, Book, Member, Order


# Create your views here.
def index(request):
    response = HttpResponse()

    # Display books ordered by primary key (id)
    booklist = Book.objects.all().order_by('id')
    heading1 = '<p><strong>List of available books (ordered by ID):</strong></p>'
    response.write(heading1)
    for book in booklist:
        para = '<p>' + str(book.id) + ': ' + str(book) + '</p>'
        response.write(para)

    # Add spacing
    response.write('<br><hr><br>')

    # Display publishers ordered by city (descending)
    publisherlist = Publisher.objects.all().order_by('-city')
    heading2 = '<p><strong>List of Publishers (ordered by city, descending):</strong></p>'
    response.write(heading2)
    for publisher in publisherlist:
        para = '<p>' + publisher.name + ' - ' + publisher.city + '</p>'
        response.write(para)

    return response


def about(request):
    response = HttpResponse()
    response.write('<p>This is an eBook APP.</p>')
    response.write('<p><strong>Student ID:</strong> 110192211</p>')
    return response


def detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    response = HttpResponse()

    # Display book title in uppercase
    title_line = '<p><strong>Title:</strong> ' + book.title.upper() + '</p>'
    response.write(title_line)

    # Display price with $ symbol
    price_line = '<p><strong>Price:</strong> $' + str(book.price) + '</p>'
    response.write(price_line)

    # Display publisher
    publisher_line = '<p><strong>Publisher:</strong> ' + book.publisher.name + '</p>'
    response.write(publisher_line)

    return response
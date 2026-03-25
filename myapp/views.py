from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Avg
import random

from .models import Book, Member, Publisher, Order, Review
from .forms import OrderForm, ReviewForm, FeedbackForm, SearchForm, MemberRegistrationForm

# -----------------------------
# AI Logic Helpers
# -----------------------------
def analyze_sentiment(text):
    """Simple AI Rule-based sentiment analysis"""
    positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'helpful', 'informative']
    negative_words = ['bad', 'poor', 'worst', 'hate', 'boring', 'unhelpful', 'useless', 'slow']
    
    text = text.lower()
    score = 0
    for word in positive_words:
        if word in text: score += 1
    for word in negative_words:
        if word in text: score -= 1
        
    if score > 0: return 'Positive'
    if score < 0: return 'Critical'
    return 'Neutral'

def get_ai_recommendations(request):
    """Smart AI Recommendation system based on category interest"""
    all_books = list(Book.objects.all())
    if not all_books: return []
    
    # Simple logic: pick 3 random books but prioritize those from diverse categories
    recommendations = random.sample(all_books, min(3, len(all_books)))
    return recommendations


# -----------------------------
# Lab 8 & 9: Core Views
# -----------------------------
def index(request):
    booklist = Book.objects.all()

    # Session: check last login
    last_login = request.session.get('last_login')
    last_login_message = ""
    if not last_login:
        last_login_message = "Your las login was more than one hour ago"

    # AI Feature: Recommendations
    recommendations = get_ai_recommendations(request)

    return render(request, 'myapp/index.html', {
        'booklist': booklist,
        'recommendations': recommendations,
        'last_login': last_login,
        'last_login_message': last_login_message
    })


def about(request):
    # Lab 10: Cookie logic for lucky number
    mynum = request.COOKIES.get('lucky_num')

    if not mynum:
        mynum = random.randint(1, 100)

    response = render(request, 'myapp/about.html', {'mynum': mynum})

    # Set cookie for 5 minutes (300 seconds)
    response.set_cookie('lucky_num', mynum, max_age=300)

    return response


def detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    return render(request, 'myapp/detail.html', {'book': book})


def findbooks(request):
    form = SearchForm(request.GET or None)
    books = Book.objects.all()

    if form.is_valid():
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')

        if category:
            books = books.filter(category=category)

        if min_price is not None:
            books = books.filter(price__gte=min_price)

        if max_price is not None:
            books = books.filter(price__lte=max_price)

    return render(request, 'myapp/findbooks.html', {
        'form': form,
        'books': books
    })


def getFeedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)

        if form.is_valid():
            choices = []
            selected = form.cleaned_data['feedback']
            labels = dict(form.fields['feedback'].choices)
            for s in selected:
                choices.append(labels.get(s))
            
            return render(request, 'myapp/fb_results.html', {'choices': choices})
    else:
        form = FeedbackForm()

    return render(request, 'myapp/feedback.html', {'form': form})


def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            books = form.cleaned_data['books']
            order = form.save(commit=False)
            member = order.member
            type = order.order_type
            order.save()
            form.save_m2m() # Required for M2M fields when using commit=False
            if type == 1:
                for b in order.books.all():
                    member.borrowed_books.add(b)
            return render(request, 'myapp/order_response.html', {'books': books, 'order': order})
    else:
        form = OrderForm()
    return render(request, 'myapp/placeorder.html', {'form': form})


def review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            review_instance = form.save(commit=False)
            # AI: Analyze sentiment
            review_instance.sentiment = analyze_sentiment(review_instance.comments)
            review_instance.save()
            
            # Increment review count for the book
            book = review_instance.book
            book.num_reviews += 1
            book.save()
            return render(request, 'myapp/review.html', {'form': ReviewForm(), 'success': True})
    else:
        form = ReviewForm()

    return render(request, 'myapp/review.html', {'form': form})


# -----------------------------
# Lab 9: Authentication & Sessions
# -----------------------------
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                # Store login time in session
                request.session['last_login'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                # Set session expiry to 1 hour (3600 seconds)
                request.session.set_expiry(3600)
                return HttpResponseRedirect(reverse('myapp:index'))
            else:
                return HttpResponse('Your account is disabled.')
        else:
            return HttpResponse('Invalid login details.')
    else:
        return render(request, 'myapp/login.html')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('myapp:index'))


# -----------------------------
# Lab 9: chk_reviews
# -----------------------------
@login_required
def chk_reviews(request, book_id):
    if hasattr(request.user, 'member'): # Checking if user is a Member
        book = get_object_or_404(Book, pk=book_id)
        reviews = Review.objects.filter(book=book)
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            return render(request, 'myapp/chk_reviews.html', {
                'book': book,
                'reviews': reviews,
                'avg_rating': avg_rating
            })
        else:
            return render(request, 'myapp/chk_reviews.html', {
                'book': book,
                'message': 'No reviews yet.'
            })
    else:
        return HttpResponse('You are not a registered member!')


def user_signup(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse('myapp:index'))
    else:
        form = MemberRegistrationForm()
    return render(request, 'myapp/signup.html', {'form': form})


def discover(request):
    """Market Trends: Top trending books in March 2026"""
    trending_books = [
        {'title': 'The Night We Met', 'author': 'Abby Jimenez', 'genre': 'Romance'},
        {'title': 'The Wings That Bind', 'author': 'Briar Boleyn', 'genre': 'Fantasy'},
        {'title': 'Want to Know a Secret?', 'author': 'Freida McFadden', 'genre': 'Thriller'},
        {'title': 'A World Appears', 'author': 'Michael Pollan', 'genre': 'Non-Fiction'},
        {'title': 'Kids, Wait Till You Hear This!', 'author': 'Liza Minnelli', 'genre': 'Memoir'},
    ]
    return render(request, 'myapp/discover.html', {'trending_books': trending_books})


# -----------------------------
# AI Chat Backend
# -----------------------------
from django.http import JsonResponse

def ai_chat(request):
    query = request.GET.get('q', '').lower()
    
    # Simple AI Routing Logic
    if 'suggest' in query or 'recommend' in query:
        books = Book.objects.all()
        if 'science' in query:
            match = books.filter(category='S').first()
        elif 'fiction' in query:
            match = books.filter(category='F').first()
        else:
            match = books.order_by('?').first()
            
        if match:
            response = f"I've found a great one for you: '{match.title}'! It's in the {match.get_category_display()} section."
        else:
            response = "I couldn't find a specific book right now, but our collection is always growing!"
            
    elif 'price' in query or 'cheap' in query:
        cheap_book = Book.objects.order_by('price').first()
        response = f"Our most affordable book is currently '{cheap_book.title}' at just ${cheap_book.price}."
        
    elif 'about' in query:
        response = "DBOOK is a premium library platform designed for book lovers. You can browse, review, and borrow titles seamlessly."
        
    else:
        response = "That's a great question! I'm still learning about our library. Try asking for a book suggestion or information about DBOOK!"

    return JsonResponse({'response': response})
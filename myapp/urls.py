from django.urls import path
from myapp import views

app_name = 'myapp'

urlpatterns = [
    # Home & basic pages
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),

    # Book-related
    path('<int:book_id>/', views.detail, name='detail'),
    path('chk_reviews/<int:book_id>/', views.chk_reviews, name='chk_reviews'),

    # Features
    path('findbooks/', views.findbooks, name='findbooks'),
    path('place_order/', views.place_order, name='place_order'),
    path('review/', views.review, name='review'),
    path('feedback/', views.getFeedback, name='feedback1'),

    # Authentication (Lab 9)
    path('login/', views.user_login, name='user_login'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('user_signup/', views.user_signup, name='user_signup'),
    path('ai_chat/', views.ai_chat, name='ai_chat'),
    path('discover/', views.discover, name='discover'),
    path('my_wishlist/', views.my_wishlist, name='my_wishlist'),
    path('toggle_wishlist/<int:book_id>/', views.toggle_wishlist, name='toggle_wishlist'),
]
from django.db import models
import datetime
from django.contrib.auth.models import User
from django.utils import timezone


class Publisher(models.Model):
    """Publisher model for book publishers"""
    name = models.CharField(max_length=200)
    website = models.URLField()
    city = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, default='Canada')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Book(models.Model):
    """Book model with category choices"""
    CATEGORY_CHOICES = [
        ('S', 'Science&Tech'),
        ('F', 'Fiction'),
        ('B', 'Biography'),
        ('T', 'Travel'),
        ('O', 'Other')
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default='S')
    num_pages = models.PositiveIntegerField(default=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    publisher = models.ForeignKey(Publisher, related_name='books', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    num_reviews = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

    class Meta:
        ordering = ['title']


class Member(User):
    """Member model extending Django's User model"""
    STATUS_CHOICES = [
        (1, 'Regular member'),
        (2, 'Premium Member'),
        (3, 'Guest Member'),
    ]

    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=20, default='Windsor')
    province = models.CharField(max_length=2, default='ON')
    last_renewal = models.DateField(default=timezone.now)
    auto_renew = models.BooleanField(default=True)
    borrowed_books = models.ManyToManyField(Book, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Member'


class Order(models.Model):
    """Order model for book purchases and borrowing"""
    ORDER_TYPE_CHOICES = [
        (0, 'Purchase'),
        (1, 'Borrow'),
    ]

    books = models.ManyToManyField(Book)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='orders')
    order_type = models.IntegerField(choices=ORDER_TYPE_CHOICES, default=1)
    order_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Order #{self.id} - {self.member.first_name} {self.member.last_name}"

    def total_items(self):
        """Returns total number of books in the order"""
        return self.books.count()

    class Meta:
        ordering = ['-order_date']


class Review(models.Model):
    """Review model for book reviews"""
    reviewer = models.EmailField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comments = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Review for {self.book.title} by {self.reviewer}"
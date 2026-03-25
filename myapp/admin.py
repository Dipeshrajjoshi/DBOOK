from django.contrib import admin
from .models import Publisher, Book, Member, Order

# Register your models here.
admin.site.register(Publisher)

class BookAdmin(admin.ModelAdmin):
    fields = [('title', 'category', 'publisher'), ('num_pages', 'price', 'num_reviews')]
    list_display = ('title', 'category', 'price','num_pages')

admin.site.register(Book, BookAdmin)

# Member already has Meta verbose_name = 'Member' in models.py
admin.site.register(Member)

class OrderAdmin(admin.ModelAdmin):
    # a. The fields to be displayed for each object: ‘books’ on first line; 'member', 'order_type', and 'order_date' on second line.
    fields = ['books', ('member', 'order_type', 'order_date')]
    # b. Change list should show attributes: ‘id’, ‘member’, 'order_type', and 'order_date'. It should also indicate total number of books in the order.
    # total_items is defined in models.Order class
    list_display = ('id', 'member', 'order_type', 'order_date', 'total_items')

admin.site.register(Order, OrderAdmin)
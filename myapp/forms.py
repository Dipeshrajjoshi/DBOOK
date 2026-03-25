from django import forms
from django.contrib.auth.forms import UserCreationForm
from myapp.models import Order, Review, Book, Member

class FeedbackForm(forms.Form):
    FEEDBACK_CHOICES = [
        ('B', 'Borrow'),
        ('P', 'Purchase'),
    ]
    feedback = forms.MultipleChoiceField(
        choices=FEEDBACK_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )

class SearchForm(forms.Form):
    name = forms.CharField(
        label='Your Name',
        max_length=100,
        required=False
    )
    category = forms.ChoiceField(
        label='Select a category:',
        choices=[
            ('', '-- All Categories --'),
            ('S', 'Science&Tech'),
            ('F', 'Fiction'),
            ('B', 'Biography'),
            ('T', 'Travel'),
            ('O', 'Other'),
        ],
        required=False
    )
    max_price = forms.IntegerField(
        label='Maximum Price',
        min_value=0,
        required=True
    )

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['books', 'member', 'order_type']
        widgets = {
            'books': forms.CheckboxSelectMultiple(),
            'order_type': forms.RadioSelect
        }
        labels = {
            'member': u'Member name',
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['reviewer', 'book', 'rating', 'comments']
        widgets = {
            'book': forms.RadioSelect
        }
        labels = {
            'reviewer': 'Please enter a valid email',
            'rating': 'Rating: An integer between 1 (worst) and 5 (best)',
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is not None and (rating < 1 or rating > 5):
            raise forms.ValidationError('Rating must be between 1 and 5.')
        return rating

class MemberRegistrationForm(UserCreationForm):
    class Meta:
        model = Member
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'address', 'city', 'province')
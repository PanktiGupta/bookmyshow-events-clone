from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['customer_name', 'email', 'phone', 'seats']
        widgets = {
            'customer_name': forms.TextInput(attrs={'placeholder': 'Full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '10-digit mobile number'}),
            'seats': forms.NumberInput(attrs={'min': 1, 'max': 10}),
        }

    def __init__(self, *args, event=None, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_seats(self):
        seats = self.cleaned_data['seats']
        if self.event and seats > self.event.seats_available:
            raise forms.ValidationError('Only %(count)s seats are available.', params={'count': self.event.seats_available})
        return seats


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

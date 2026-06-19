from django.conf import settings  # type: ignore
from django.db import models
from datetime import time
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
class Event(models.Model):
    CATEGORY_CHOICES = [
        ('Music','Music'),
        ('Sports','Sports'),
        ('Comedy','Comedy'),
        ('Movies','Movies'),
        ('Theatre','Theatre'),
        ('Tech','Tech')
    ]

    title = models.CharField(max_length=200)
    image = models.CharField(max_length=200)  # just store image file name
    date = models.DateField()
    time = models.TimeField(default=time(19, 0))
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=200)
    city = models.CharField(max_length=100, default='Bhopal')
    venue = models.CharField(max_length=200, default='Main Auditorium')
    price = models.IntegerField()
    seats_available = models.PositiveIntegerField(default=100)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal('4.5'),
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    language = models.CharField(max_length=80, default='Hindi, English')
    duration = models.CharField(max_length=50, default='2h 30m')
    is_featured = models.BooleanField(default=False)
    description = models.TextField()

    class Meta:
        ordering = ['date', 'time', 'title']

    @property
    def image_url(self):
        if self.image.startswith(('http://', 'https://', '/')):
            return self.image

        fallback_images = {
            'Music': 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=900&q=80',
            'Sports': 'https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?auto=format&fit=crop&w=900&q=80',
            'Comedy': 'https://images.unsplash.com/photo-1527224538127-2104bb71c51b?auto=format&fit=crop&w=900&q=80',
            'Movies': 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=900&q=80',
            'Theatre': 'https://images.unsplash.com/photo-1503095396549-807759245b35?auto=format&fit=crop&w=900&q=80',
            'Tech': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=900&q=80',
        }
        return fallback_images.get(self.category, fallback_images['Movies'])

    def __str__(self):
        return self.title


class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='bookings',
        blank=True,
        null=True,
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    seats = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    total_amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    booked_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-booked_at']

    def __str__(self):
        return f'{self.customer_name} - {self.event.title}'

    @property
    def transaction_id(self):
        return f'TXN{self.pk:06d}'

class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
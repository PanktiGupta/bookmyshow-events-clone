from django.contrib import admin

from .models import Booking, Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'city', 'date', 'time', 'price', 'seats_available', 'is_featured')
    list_filter = ('category', 'city', 'is_featured', 'date')
    search_fields = ('title', 'venue', 'location', 'city')
    list_editable = ('price', 'seats_available', 'is_featured')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'event', 'seats', 'total_amount', 'booked_at')
    list_filter = ('booked_at', 'event__category', 'event__city')
    search_fields = ('customer_name', 'email', 'phone', 'event__title')

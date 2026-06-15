from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    booked_seats = serializers.IntegerField(source='bookings.count', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'image', 'date', 'time', 'category', 'city',
            'location', 'venue', 'price', 'seats_available', 'rating',
            'language', 'duration', 'is_featured', 'description', 'booked_seats'
        ]

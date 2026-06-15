from datetime import date, time

from django.test import TestCase
from django.urls import reverse

from .models import Booking, Event


class EventFlowTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title='Indie Night Live',
            image='https://images.unsplash.com/photo-1492684223066-81342ee5ff30',
            date=date(2026, 7, 20),
            time=time(19, 30),
            category='Music',
            location='Lake View Road',
            city='Bhopal',
            venue='Open Air Arena',
            price=799,
            seats_available=25,
            rating=4.7,
            language='Hindi, English',
            duration='2h',
            is_featured=True,
            description='A premium live music event.',
        )

    def test_events_page_lists_events(self):
        response = self.client.get(reverse('events'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Indie Night Live')
        self.assertContains(response, 'Apply Filters')

    def test_event_detail_page_loads(self):
        response = self.client.get(reverse('event_detail', args=[self.event.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Book tickets')

    def test_wishlist_toggle_saves_event_id_in_session(self):
        response = self.client.get(reverse('wishlist', args=[self.event.pk]))

        self.assertRedirects(response, '/')
        self.assertEqual(self.client.session['wishlist'], [self.event.pk])

    def test_booking_creates_booking_and_reduces_available_seats(self):
        response = self.client.post(
            reverse('book_event', args=[self.event.pk]),
            {
                'customer_name': 'Aarav Sharma',
                'email': 'aarav@example.com',
                'phone': '9876543210',
                'seats': 3,
            },
        )

        booking = Booking.objects.get()
        self.event.refresh_from_db()

        self.assertRedirects(response, reverse('booking_success', args=[booking.pk]))
        self.assertEqual(booking.total_amount, 2397)
        self.assertEqual(self.event.seats_available, 22)

    def test_booking_rejects_more_seats_than_available(self):
        response = self.client.post(
            reverse('book_event', args=[self.event.pk]),
            {
                'customer_name': 'Aarav Sharma',
                'email': 'aarav@example.com',
                'phone': '9876543210',
                'seats': 30,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Only 25 seats are available.')
        self.assertFalse(Booking.objects.exists())

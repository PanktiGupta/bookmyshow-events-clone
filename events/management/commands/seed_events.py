from datetime import date, time

from django.core.management.base import BaseCommand

from events.models import Event


class Command(BaseCommand):
    help = 'Create sample BookMyShow-style events for local development.'

    def handle(self, *args, **options):
        events = [
            {
                'title': 'Arijit Singh Live Concert',
                'image': 'concert.jpg',
                'date': date(2026, 7, 10),
                'time': time(19, 0),
                'category': 'Music',
                'location': 'JLN Stadium Road',
                'city': 'Delhi',
                'venue': 'Jawaharlal Nehru Stadium',
                'price': 1499,
                'seats_available': 100,
                'rating': 4.8,
                'language': 'Hindi',
                'duration': '3h',
                'is_featured': True,
                'description': 'A grand live concert with soulful Bollywood music and premium stage production.',
            },
            {
                'title': 'Stand-up Comedy Night',
                'image': 'comedy.jpg',
                'date': date(2026, 7, 15),
                'time': time(20, 0),
                'category': 'Comedy',
                'location': 'Bandra West',
                'city': 'Mumbai',
                'venue': 'The Laugh Club',
                'price': 499,
                'seats_available': 100,
                'rating': 4.4,
                'language': 'Hindi, English',
                'duration': '1h 45m',
                'is_featured': True,
                'description': 'A sharp, fast-paced comedy evening with top touring comics.',
            },
            {
                'title': 'IPL Final Screening',
                'image': 'cricket.jpg',
                'date': date(2026, 7, 20),
                'time': time(18, 30),
                'category': 'Sports',
                'location': 'MG Road',
                'city': 'Bangalore',
                'venue': 'Arena Sports Bar',
                'price': 299,
                'seats_available': 100,
                'rating': 4.3,
                'language': 'Hindi, English',
                'duration': '4h',
                'is_featured': False,
                'description': 'Big-screen cricket with stadium-like crowd energy, food combos, and fan zones.',
            },
            {
                'title': 'Tech Conference 2026',
                'image': 'tech.jpg',
                'date': date(2026, 8, 1),
                'time': time(10, 0),
                'category': 'Tech',
                'location': 'HITEC City',
                'city': 'Hyderabad',
                'venue': 'Cyber Convention Centre',
                'price': 999,
                'seats_available': 100,
                'rating': 4.6,
                'language': 'English',
                'duration': '7h',
                'is_featured': False,
                'description': 'A full-day technology summit with AI, cloud, startups, and product sessions.',
            },
            {
                'title': 'Hamilton Theatre Experience',
                'image': 'theatre.jpg',
                'date': date(2026, 8, 8),
                'time': time(18, 0),
                'category': 'Theatre',
                'location': 'Shivaji Nagar',
                'city': 'Pune',
                'venue': 'Royal Opera House',
                'price': 1299,
                'seats_available': 100,
                'rating': 4.7,
                'language': 'English',
                'duration': '2h 40m',
                'is_featured': True,
                'description': 'A premium theatre production with live music, dramatic staging, and reserved seating.',
            },
        ]

        created = 0
        for event_data in events:
            _, was_created = Event.objects.get_or_create(
                title=event_data['title'],
                defaults=event_data,
            )
            created += int(was_created)

        self.stdout.write(self.style.SUCCESS(f'Seed complete. Created {created} events.'))

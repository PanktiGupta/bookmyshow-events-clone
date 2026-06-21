
import logging
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q, Sum
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Booking, Event
from .forms import BookingForm, RegisterForm
from django.contrib.auth import get_user_model
from .utils import generate_otp, store_otp, set_resend_lock, can_resend
from .utils import get_otp, delete_otp
from .serializers import EventSerializer
from django.template.loader import render_to_string
User = get_user_model()
logger = logging.getLogger(__name__)

def _wishlist(request):
    return [int(event_id) for event_id in request.session.get('wishlist', [])]


def _event_filters(request):
    return {
        'query': request.GET.get('q', '').strip(),
        'category': request.GET.get('category', '').strip(),
        'city': request.GET.get('city', '').strip(),
        'price': request.GET.get('price', '').strip(),
    }


def _apply_filters(events, filters):
    if filters['query']:
        events = events.filter(
            Q(title__icontains=filters['query'])
            | Q(description__icontains=filters['query'])
            | Q(venue__icontains=filters['query'])
            | Q(location__icontains=filters['query'])
        )

    if filters['category']:
        events = events.filter(category__iexact=filters['category'])

    if filters['city']:
        events = events.filter(city__iexact=filters['city'])

    if filters['price'] == 'budget':
        events = events.filter(price__lt=500)
    elif filters['price'] == 'standard':
        events = events.filter(price__gte=500, price__lte=1200)
    elif filters['price'] == 'premium':
        events = events.filter(price__gt=1200)

    return events


def _catalog_context(request, events):
    wishlist = _wishlist(request)
    return {
        'events': events,
        'wishlist': wishlist,
        'categories': Event.CATEGORY_CHOICES,
        'cities': Event.objects.order_by('city').values_list('city', flat=True).distinct().order_by('city'),
        'filters': _event_filters(request),
    }


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    wishlist = _wishlist(request)
    similar_events = Event.objects.filter(
        category=event.category
    ).exclude(id=event.pk)[:4]

    return render(request, 'event_detail.html', {
        'event': event,
        'wishlist': wishlist,
        'similar_events': similar_events,
    })


def events_page(request):
    events = _apply_filters(Event.objects.all(), _event_filters(request))
    return render(request, 'events.html', _catalog_context(request, events))

def payment(request):
    # my payment logic here
    pass


def home(request):
    filters = _event_filters(request)
    events = _apply_filters(Event.objects.all(), filters)
    featured_events = Event.objects.filter(is_featured=True)[:6]
    if not featured_events:
        featured_events = Event.objects.all()[:6]

    bookings_count = Booking.objects.count()
    revenue = Booking.objects.aggregate(total=Sum('total_amount'))['total'] or 0

    context = _catalog_context(request, events[:10])
    context.update({
        'featured_events': featured_events,
        'bookings_count': bookings_count,
        'revenue': revenue,
    })
    return render(request, 'home.html', context)


def wishlist_page(request):
    events = Event.objects.filter(id__in=_wishlist(request))
    return render(request, 'wishlist.html', _catalog_context(request, events))


def toggle_wishlist(request, event_id):
    get_object_or_404(Event, id=event_id)
    wishlist = _wishlist(request)
    if event_id in wishlist:
        wishlist.remove(event_id)
        messages.info(request, 'Removed from wishlist.')
    else:
        wishlist.append(event_id)
        messages.success(request, 'Added to wishlist.')

    request.session['wishlist'] = wishlist
    return redirect(request.META.get('HTTP_REFERER', '/'))


def book_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if not request.user.is_authenticated:
        messages.info(request, 'Please login to book tickets and view them in your profile.')
        return redirect(f'/login/?next=/events/{event.pk}/book/')

    if request.method == 'POST':
        form = BookingForm(request.POST, event=event)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.event = event
            booking.total_amount = booking.seats * event.price
            booking.save()

            event.seats_available -= booking.seats
            event.save(update_fields=['seats_available'])

            messages.success(request, 'Booking confirmed successfully.')
            return redirect('booking_success', booking_id=booking.pk)
    else:
        form = BookingForm(
            event=event,
            initial={
                'customer_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
        )

    return render(request, 'booking.html', {'event': event, 'form': form})


def booking_success(request, booking_id):
    booking = get_object_or_404(Booking.objects.select_related('event', 'user'), id=booking_id)
    if booking.user and booking.user != request.user:
        messages.error(request, 'You cannot view another user booking.')
        return redirect('profile')
    return render(request, 'booking_success.html', {'booking': booking})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()

        if not user.is_active:
            messages.error(request, 'Please verify your email first.')
            return redirect('verify_otp')

        login(request, user)
        messages.success(request, 'Logged in successfully.')
        return redirect(request.GET.get('next') or 'profile')

    return render(request, 'login.html', {'form': form})


def _send_otp_email(email, otp):
    if not settings.OTP_EMAIL_ENABLED:
        return False

    html_content = render_to_string(
        "emails/otp_email.html",
        {"otp": otp}
    )

    message = EmailMultiAlternatives(
        "Verify Your Account - BookMyShow Pro",
        "",
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )
    message.attach_alternative(html_content, "text/html")
    message.send()
    return True


def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        # if username or email:
        #     User.objects.filter(
        #         Q(username=username) | Q(email=email),
        #         is_active=False,
        #     ).delete()
    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        otp = generate_otp()
        user_email = form.cleaned_data['email']

        try:
            with transaction.atomic():
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                store_otp(user_email, otp)
        except Exception:
            logger.exception("Failed to create registration for %s", user_email)
            form.add_error(
                None,
                'Could not create your account. Please try again.'
            )
            delete_otp(user_email)
            return render(request, 'register.html', {'form': form})

        try:
            email_sent = _send_otp_email(user_email, otp)
        except Exception:
            logger.exception("Failed to send registration OTP to %s", user_email)
            email_sent = False

        if not email_sent:
            request.session['dev_otp'] = otp
        else:
            request.session.pop('dev_otp', None)

        request.session['email'] = user_email

        if email_sent:
            messages.success(request, 'OTP sent to your email.')
        else:
            messages.info(request, 'Email OTP is not configured on the server. Use the OTP shown below to verify.')
        return redirect('verify_otp')

    return render(request, 'register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('home')


@login_required(login_url='login')
def profile(request):
    bookings = Booking.objects.select_related('event').filter(user=request.user)
    confirmed_bookings = bookings.filter(status='confirmed')
    cancelled_bookings = bookings.filter(status='cancelled')
    total_spent = confirmed_bookings.aggregate(total=Sum('total_amount'))['total'] or 0

    return render(request, 'profile.html', {
        'bookings': bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_spent': total_spent,
    })

@login_required(login_url='login')
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking.objects.select_related('event'), id=booking_id, user=request.user)

    if booking.status == 'cancelled':
        messages.info(request, 'This ticket is already cancelled.')
        return redirect('profile')

    booking.status = 'cancelled'
    booking.cancelled_at = timezone.now()
    booking.save(update_fields=['status', 'cancelled_at'])

    booking.event.seats_available += booking.seats
    booking.event.save(update_fields=['seats_available'])

    messages.success(request, 'Ticket cancelled and seats released.')
    return redirect('profile')


@api_view(['GET'])
def event_api(request):
    events = _apply_filters(Event.objects.all(), _event_filters(request))
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

def verify_otp(request):
    email = request.session.get('email')
    dev_otp = request.session.get('dev_otp')

    if request.method == "POST":
        otp_entered = request.POST['otp']
        real_otp = get_otp(email)

        if real_otp and real_otp == otp_entered:
            User = get_user_model()
            user = User.objects.filter(email=email).order_by('-id').first()
            if not user:
                messages.error(request, "No account found for that email.")
                return redirect('register')
            user.is_active = True
            user.save()

            delete_otp(email)
            request.session.pop('dev_otp', None)

            messages.success(request, "Email verified successfully.")
            return redirect('login')

        return render(request, "verify_otp.html", {"error": "Invalid OTP", "dev_otp": dev_otp})

    return render(request, "verify_otp.html", {"identifier": email, "dev_otp": dev_otp})

def resend_otp(request):
    print("=== RESEND OTP CALLED ===")

    email = request.session.get('email')
    print("EMAIL:", email)

    if not email:
        print("NO EMAIL IN SESSION")
        return redirect('register')

    print("CAN RESEND:", can_resend(email))

    if not can_resend(email):
        print("BLOCKED")
        return render(
            request,
            "verify_otp.html",
            {"error": "Wait 30 seconds before resending OTP"}
        )

    otp = generate_otp()
    store_otp(email, otp)

    print("SENDING OTP:", otp)

    try:
        email_sent = _send_otp_email(email, otp)
    except Exception:
        logger.exception("Failed to resend OTP to %s", email)
        email_sent = False

    if not email_sent:
        request.session['dev_otp'] = otp
    else:
        request.session.pop('dev_otp', None)

    set_resend_lock(email)

    print("LOCK VALUE:", cache.get(f"resend_lock:{email}"))

    return render(
        request,
        "verify_otp.html",
        {
            "message": "OTP resent successfully" if email_sent else "Email OTP is not configured on the server. Use the OTP shown below.",
            "identifier": email,
            "dev_otp": None if email_sent else otp,
        }
    )

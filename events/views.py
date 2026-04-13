from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Event
from .serializers import EventSerializer
def event_detail(request, id):
    event = Event.objects.get(id=id)
    wishlist = request.session.get('wishlist', [])

    return render(request, 'event_detail.html', {
        'event': event,
        'wishlist': wishlist
    })

def events_page(request):
    category = request.GET.get('category')
    price = request.GET.get('price')

    events = Event.objects.all()

    if category:
        events = events.filter(category__iexact=category)

    if price == 'low':
        events = events.filter(price__lt=500)
    elif price == 'mid':
        events = events.filter(price__gte=500, price__lte=1000)
    elif price == 'high':
        events = events.filter(price__gt=1000)

    wishlist = request.session.get('wishlist', [])

    return render(request, 'events.html', {
        'events': events,
        'wishlist': wishlist
    })

def home(request):
    query = request.GET.get('q')

    if query:
        events = Event.objects.filter(title__icontains=query)
    else:
        events = Event.objects.all()

    wishlist = request.session.get('wishlist', [])

    return render(request, 'home.html', {
        'events': events,
        'wishlist': wishlist
    })


def toggle_wishlist(request, event_id):
    wishlist = request.session.get('wishlist', [])

    if event_id in wishlist:
        wishlist.remove(event_id)
    else:
        wishlist.append(event_id)

    request.session['wishlist'] = wishlist
    return redirect('/')


@api_view(['GET'])
def event_api(request):
    events = Event.objects.all()
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Event
from .serializers import EventSerializer

def events_page(request):
    events = Event.objects.all()
    return render(request, 'events.html', {'events': events})

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

# ...existing code...

# def events_page(request):
#     category = request.GET.get('category')

#     if category:
#         events = Event.objects.filter(category=category)
#     else:
#         events = Event.objects.all()

#     return render(request, 'events.html', {
#         'events': events
#     })
# # ...existing code..

# API
@api_view(['GET'])
def event_api(request):
    events = Event.objects.all()
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


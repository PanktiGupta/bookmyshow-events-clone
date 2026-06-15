"""
URL configuration for bookmyshow_clone project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from events import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Homepage
    path('', views.home, name='home'),

    # Events page
    path('events/', views.events_page, name='events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/book/', views.book_event, name='book_event'),
    path('booking/<int:booking_id>/success/', views.booking_success, name='booking_success'),
    # Wishlist
    path('wishlist/', views.wishlist_page, name='wishlist_page'),
    path('wishlist/<int:event_id>/', views.toggle_wishlist, name='wishlist'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),

    # API
    path('api/events/', views.event_api, name='api'),
]


from django.urls import path


from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.events_page, name='events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/book/', views.book_event, name='book_event'),
    # path('booking/<int:booking_id>/payment/', views.payment, name='payment'),
    path('booking/<int:booking_id>/success/', views.booking_success, name='booking_success'),
    path('wishlist/', views.wishlist_page, name='wishlist_page'),
    path('wishlist/<int:event_id>/', views.toggle_wishlist, name='wishlist'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),

]


from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('', views.events_page, name='events'),
    path('events/', views.events_page, name='events'),
]

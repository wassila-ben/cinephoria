from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('details', views.details, name='details'),
    path('films', views.films, name = 'films' ),
    path('reservation', views.reservation, name = 'reservation' ),
    path('contact', views.contact, name = 'contact' ),
    path('login', views.login, name = 'login' ),
]
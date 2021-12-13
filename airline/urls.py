from django.urls import path
from . import views

urlpatterns = [
    path('', views.airlinehome, name="airlinehome"),
    path('schedule', views.workdeltschedule, name="deltaschedule"),
]
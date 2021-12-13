from django.urls import path
from . import views

urlpatterns = [
    path('', views.airporthome, name="airporthome"),
    path('sunriseset', views.sunriseset, name="sunriseset"),
    path('searchairport', views.searchairport, name="searchairport"),
    path('<str:icao>',views.airporturl, name="gettingairport")
]
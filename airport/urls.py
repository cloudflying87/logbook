from django.urls import path
from airport.views import AirportLookup, SearchAirport, airporthome, sunriseset,airporturl

urlpatterns = [
    path('', airporthome, name="airporthome"),
    path('sunriseset', sunriseset, name="sunriseset"),
    path('searchairport', SearchAirport.as_view(), name="searchairport"),
    path('airportlookup', AirportLookup.as_view(), name="airportlookup"),
    path('<str:icao>',airporturl, name="gettingairport"),
    
]
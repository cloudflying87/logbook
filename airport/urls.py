from django.urls import path
from airport.views import FlightMap, AirportLookup, SearchAirport, airporthome, sunriseset,airporturl,drawmap

urlpatterns = [
    path('', airporthome, name="airporthome"),
    path('sunriseset', sunriseset, name="sunriseset"),
    path('searchairport', SearchAirport.as_view(), name="searchairport"),
    path('airportlookup', AirportLookup.as_view(), name="airportlookup"),
    path('map', FlightMap.as_view(), name="flightmap"),
    path('drawmap', drawmap, name="drawmap"),
    path('<str:icao>',airporturl, name="gettingairport"),
    
]
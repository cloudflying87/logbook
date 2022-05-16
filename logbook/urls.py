from django.urls import path
from logbook.views import AirportAutoComplete, LogbookEntry,AircraftIDLookup
from . import views

urlpatterns = [
    
    path('entry', LogbookEntry.as_view(), name="logbookhome"),
    path('autocomplete/', AirportAutoComplete.as_view(),name='autocomplete'),
    path('aircraftidlookup/', AircraftIDLookup.as_view(),name='aircraftidlookup')
]
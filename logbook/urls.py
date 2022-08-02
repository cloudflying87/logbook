from django.urls import path
from logbook.views import AirportAutoComplete, LogbookEntry,AircraftIDLookup,LogbookDisply


urlpatterns = [
    path('', LogbookDisply.as_view(), name="logbookdisplay"),
    path('entry', LogbookEntry.as_view(), name="logbookhome"),
    path('autocomplete/', AirportAutoComplete.as_view(),name='autocomplete'),
    path('aircraftidlookup/', AircraftIDLookup.as_view(),name='aircraftidlookup')
]
from django.urls import path
from logbook.views import AirportAutoComplete, LogbookEntry,AircraftIDLookup,LogbookDisply, EditEntry, ViewEntry


urlpatterns = [
    path('', LogbookDisply.as_view(), name="logbookdisplay"),
    path('entry', LogbookEntry.as_view(), name="logbookhome"),
    path('view/<int:id>', ViewEntry.as_view(), name = "viewentry"),
    path('edit/<int:id>', EditEntry.as_view(), name = "entryupdate"),
    path('autocomplete/', AirportAutoComplete.as_view(),name='autocomplete'),
    path('aircraftidlookup/', AircraftIDLookup.as_view(),name='aircraftidlookup')
]
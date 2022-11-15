from django.urls import path
from logbook.views import AirportAutoComplete, LogbookEntry,AircraftIDLookup,LogbookDisply, EditEntry, ViewEntry, DeleteEntry, reworktimes, reworktimes2, summary


urlpatterns = [
    path('', LogbookDisply.as_view(), name="logbookdisplay"),
    path('entry', LogbookEntry.as_view(), name="logbookhome"),
    path('build', reworktimes, name="times"),
    path('build2', reworktimes2, name="times2"),
    path('summary/<int:id>', summary, name="summary"),
    path('view/<int:id>', ViewEntry.as_view(), name = "viewentry"),
    path('edit/<int:id>', EditEntry.as_view(), name = "entryupdate"),
    path('delete/<int:id>', DeleteEntry.as_view(), name = "DeleteEntry"),
    path('autocomplete/', AirportAutoComplete.as_view(),name='autocomplete'),
    path('aircraftidlookup/', AircraftIDLookup.as_view(),name='aircraftidlookup')
]
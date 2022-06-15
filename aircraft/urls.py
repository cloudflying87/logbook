from django.urls import path
from aircraft.views import AircraftEntry, NewIDLookup


urlpatterns = [
    path('', AircraftEntry.as_view(), name="aircrafthome"),
    path('newidlookup/', NewIDLookup.as_view(),name='newidlookup')
]
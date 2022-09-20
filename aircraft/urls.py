from django.urls import path
from aircraft.views import AircraftEntry, NewIDLookup, TailNumberLookup


urlpatterns = [
    path('', AircraftEntry.as_view(), name="aircrafthome"),
    # path('taillookup', tailnumberlookup, name='taillookup'),
    path('newidlookup/', NewIDLookup.as_view(),name='newidlookup'),
    path('taillookup/', TailNumberLookup.as_view(),name='taillookup')
]
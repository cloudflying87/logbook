from django.urls import path
from aircraft.views import AirplaneSearch,ModelIDLookup

urlpatterns = [
    path('', AirplaneSearch.as_view(), name='aircrafthome'),
    path('modellookup/', ModelIDLookup.as_view(),name='modellookup')
]
from django.urls import path
from aircraft.views import AircraftEntry, CategoryDisplay, CategoryDisplayAll, NewIDLookup, TailLookupDisplay, TailNumberLookup,TailBase


urlpatterns = [
    path('', AircraftEntry.as_view(), name="aircrafthome"),
    # path('taillookup', tailnumberlookup, name='taillookup'),
    path('newidlookup/', NewIDLookup.as_view(),name='newidlookup'),
    path('taillookup/', TailNumberLookup.as_view(),name='taillookup'),
    path('category', CategoryDisplay.as_view(), name="category"),
    path('allcategories', CategoryDisplayAll.as_view(), name="categoryall"),
    path('tail',TailBase.as_view(),name='tailbase'),
    path('taillookupdisplay', TailLookupDisplay.as_view(), name="taillookupdisplay"),
]
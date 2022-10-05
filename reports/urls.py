from django.urls import path
from reports.views import FlightAware, ReportBase, TotalsByDate, TotalsOnly, CategoryDisplay, Lookup, AirportLookup, TailLookupDisplay,TopAirports


urlpatterns = [
    path('', ReportBase.as_view(), name="reporttotals"),
    path('totals', TotalsOnly.as_view(), name="totals"),
    path('category', CategoryDisplay.as_view(), name="category"),
    path('lookup', Lookup.as_view(), name="lookup"),
    path('topairports', TopAirports.as_view(), name="topairports"),
    path('airportlookup', AirportLookup.as_view(), name="airportlookup"),
    path('taillookup', TailLookupDisplay.as_view(), name="taillookupdisplay"),
    path('flightaware', FlightAware.as_view(), name="flightaware"),
    path('datetotals', TotalsByDate.as_view(), name="totalsbydate"),
    
]
from django.urls import path
from reports.views import ReportBase, TotalsByDate, TotalsOnly, CategoryDisplay, Lookup, AirportLookup


urlpatterns = [
    path('', ReportBase.as_view(), name="reporttotals"),
    path('totals', TotalsOnly.as_view(), name="totals"),
    path('category', CategoryDisplay.as_view(), name="category"),
    path('lookup', Lookup.as_view(), name="lookup"),
    path('airportlookup', AirportLookup.as_view(), name="airportlookup"),
    path('datetotals', TotalsByDate.as_view(), name="totalsbydate"),
    
]
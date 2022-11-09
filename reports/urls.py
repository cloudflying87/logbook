from django.urls import path
from reports.views import Export,FlightAware, ReportBase, TotalsByDate, TotalsOnly, Lookup,TopAirports, exportflighttimeall, FlightawareRequest, editingFAdocument,PDFExport


urlpatterns = [
    path('', ReportBase.as_view(), name="reporttotals"),
    path('totals', TotalsOnly.as_view(), name="totals"),
    path('lookup', Lookup.as_view(), name="lookup"),
    path('topairports', TopAirports.as_view(), name="topairports"),
    path('flightaware', FlightAware.as_view(), name="flightaware"),
    path('datetotals', TotalsByDate.as_view(), name="totalsbydate"),
    path('export', Export.as_view(), name="export"),
    path('pdf', PDFExport.as_view(), name="pdf"),
    path('exportflighttime', exportflighttimeall, name="exportflighttimeall"),
    path('dates', FlightawareRequest.as_view(), name="dateselector"),
    path('editing', editingFAdocument, name="editing"),

    
]
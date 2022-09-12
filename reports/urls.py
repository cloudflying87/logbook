from django.urls import path
from reports.views import Totals, TotalsOnly, CategoryDisplay


urlpatterns = [
    path('', Totals.as_view(), name="reporttotals"),
    path('totals', TotalsOnly.as_view(), name="totals"),
    path('category', CategoryDisplay.as_view(), name="category"),
    
]
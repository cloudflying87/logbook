from django.urls import path
from reports.views import Totals


urlpatterns = [
    path('', Totals.as_view(), name="reporttotals"),
    
]
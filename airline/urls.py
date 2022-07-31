from django.urls import path
from airline.views import DeltaScheduleEntry, airlinehome

urlpatterns = [
    # path('', airlinehome, name="airlinehome"),
    path('', DeltaScheduleEntry.as_view(), name="deltaschedule"),
]
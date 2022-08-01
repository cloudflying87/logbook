from django.urls import path
from airline.views import DeltaScheduleEntry, workdeltschedulegoogle

urlpatterns = [
    path('google', workdeltschedulegoogle, name="googleschedule"),
    path('', DeltaScheduleEntry.as_view(), name="deltaschedule"),
]
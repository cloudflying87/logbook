from django.urls import path
from logbook.views import AirportAutoComplete
from . import views

urlpatterns = [
    
    path('', views.logbookhome, name="logbookhome"),
    path('test', views.testairport, name="testfunction"),
    path('autocomplete/', AirportAutoComplete.as_view(),name='autocomplete')
]
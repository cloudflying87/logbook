from django.urls import path
from . import views
from .views import logbookdisply


urlpatterns = [
    
    path('', views.logbookdisply, name="logbookdisplay"),
]
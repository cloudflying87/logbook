from django.urls import path
from . import views


urlpatterns = [
    path('', views.aircrafthome, name="aircrafthome"),
]
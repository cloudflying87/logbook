from django.urls import path
from . import views

urlpatterns = [
    path('', views.logbookhome, name="logbookhome"),
    path('test', views.testairport, name="testfunction"),
    
]
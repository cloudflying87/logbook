from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('user.urls')),
    path('users/', include('django.contrib.auth.urls')),
    path('logbook/', include('logbook.urls')),
    path('airport/', include('airport.urls')),
    path('airline/', include('airline.urls')),
    path('aircraft/', include('aircraft.urls')),
    path('reports/', include('reports.urls')),


]

from django.contrib import admin

from .models import AirlineSchedule, AirlineList

admin.site.register(AirlineList)
admin.site.register(AirlineSchedule)

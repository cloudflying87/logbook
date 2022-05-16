from django.contrib import admin

from .models import Manufacture,AircraftModel, NewPlaneMaster

admin.site.register(Manufacture)
admin.site.register(AircraftModel)
admin.site.register(NewPlaneMaster)
from django.contrib import admin

from .models import AirlineList,PayTables,PayCalculations,Rotations,BidPeriod

admin.site.register(AirlineList)
admin.site.register(PayTables)
admin.site.register(PayCalculations)
admin.site.register(Rotations)
admin.site.register(BidPeriod)


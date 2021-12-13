from django.contrib import admin

# Register your models here.
from .models import Country,Zone,Timezone,Airport

admin.site.register(Country)
admin.site.register(Zone)
admin.site.register(Timezone)
admin.site.register(Airport)
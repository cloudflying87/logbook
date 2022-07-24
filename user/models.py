from django.db import models
from airport.models import Airport
from aircraft.models import AircraftModel

class Users(models.Model):
    user_id = models.IntegerField(blank=True,null=True)
    pic = models.BooleanField(blank=True,null=True)
    sic = models.BooleanField(blank=True,null=True)
    cfi = models.BooleanField(blank=True,null=True)
    dual = models.BooleanField(blank=True,null=True)
    solo = models.BooleanField(blank=True,null=True)
    cx = models.BooleanField(blank=True,null=True)
    decimal = models.BooleanField(blank=True,null=True)
    time = models.BooleanField(blank=True,null=True)
    decimalplaces = models.IntegerField()
    defaultairport = models.ForeignKey(Airport,default ='', max_length=100,blank=True,null=True,on_delete=models.SET_DEFAULT)
    defaultairplane = models.ForeignKey(AircraftModel,default='',blank=True,null=True, on_delete=models.SET_DEFAULT)
    airlineform = models.BooleanField(blank=True,null=True)
    zulu = models.BooleanField(blank=True,null=True,default=True)

    # def __str__(self):
    #     return self
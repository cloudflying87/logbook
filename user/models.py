from django.db import models
from airline.models import AirlineList
from airport.models import Airport
from django import utils
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
    airline = models.ForeignKey(AirlineList,default ='DAL', max_length=3,on_delete=models.SET_DEFAULT)
    defaultairplane = models.ForeignKey(AircraftModel,default='',blank=True,null=True, on_delete=models.SET_DEFAULT)
    anniversarydate = models.DateField(default=utils.timezone.now)
    airlineform = models.BooleanField(blank=True,null=True)
    zulu = models.BooleanField(blank=True,null=True,default=True)
    token = models.CharField(blank=True, max_length=300)
    refresh_token = models.CharField(blank=True,null=True, max_length=300)
    token_uri = models.CharField(blank=True,null=True, max_length=300)
    client_id = models.CharField(blank=True,null=True, max_length=300)
    client_secret = models.CharField(blank=True,null=True, max_length=300)
    scopes = models.CharField(blank=True,null=True, max_length=300)
    calendarid = models.CharField(blank=True,null=True, max_length=300)
    # def __str__(self):  
    #     return str(self.user_id)
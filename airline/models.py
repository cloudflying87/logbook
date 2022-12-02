from email.policy import default
from unittest.util import _MAX_LENGTH
from aircraft.models import AircraftModel
from django.db import models
from django import utils
from tinymce import models as tinymce_models

class AirlineList(models.Model):
    airlinecode = models.CharField(primary_key=True, max_length=3)
    airlinename = models.CharField(max_length=25,blank=True,null=True)
    airlinedescription = models.CharField(max_length=200,blank=True,null=True)
    airlinesize = models.IntegerField()
    def __str__(self):
        return self.airlinecode
class PayTables(models.Model):
    effectivedate = models.DateField(default=utils.timezone.now)
    aircraft = models.CharField(max_length=30,null=True,blank=True)
    yearsofservice = models.IntegerField(default = 1)
    payamount = models.DecimalField(max_digits=8, blank=True, decimal_places=2,null=True)
    position = models.CharField(max_length=2,null=True,blank=True)
    airline = models.ForeignKey(AirlineList,default ='', max_length=100,on_delete=models.SET_DEFAULT)
    def __str__(self):
        return self.paydate,self.aircraft,self.payamount,self.position

class PayCalculations(models.Model):
    userid= models.IntegerField(default = 1)
    datecalulated = models.DateTimeField(blank=True,null=True)
    aircraftcode = models.ForeignKey(AircraftModel,default ='B737-800',on_delete=models.SET_DEFAULT)
    paycode = models.CharField(max_length=50,blank=True,null=True)
    month = models.DateField(blank=True,null=True)
    rotationid = models.CharField(max_length=50,blank=True,null=True)
    domesticblockhours = models.TimeField(blank=True,null=True)
    internationalblockhours = models.TimeField(blank=True,null=True)
    additionalpayhours = models.TimeField(blank=True,null=True)
    deadheadtime = models.TimeField(blank=True,null=True)
    minutesunder = models.TimeField(blank=True,null=True)
    airline = models.ForeignKey(AirlineList,default ='', max_length=100,on_delete=models.SET_DEFAULT)
    def __str__(self):
        return self.datecalulated,self.month

class Rotations(models.Model):
    userid= models.IntegerField(default = 1)
    rotationid = models.CharField(max_length=50,blank=True,null=True)
    rotationstart = models.DateTimeField(blank=True,null=True)
    rotationend = models.DateTimeField(blank=True,null=True)
    overnights = models.CharField(max_length=50,blank=True,null=True)
    days = models.IntegerField(default = 1)
    rotationpay = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    rotationblock = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    rotationcredit = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    scheduledtafb = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    rotationnotes = models.CharField(max_length=300,blank=True,null=True)
    micrewexportdate = models.DateTimeField(blank=True, null=True)
    googleimportdate = models.DateTimeField(blank=True, null=True)
    logbookimportdate = models.DateTimeField(default=utils.timezone.now)
    airline = models.ForeignKey(AirlineList,default ='DAL', max_length=100,on_delete=models.SET_DEFAULT,blank=True, null=True)
    rawdata = tinymce_models.HTMLField(blank=True, null=True)
    def __str__(self):
        return str(self.rotationid),str(self.rotationstart)

class BidPeriod(models.Model):
    calendarmonth = models.CharField(max_length=50,blank=True,null=True)
    bidperiodstart = models.DateField(blank=True,null=True)
    bidperiodend = models.DateField(blank=True,null=True)
    bidperioddays = models.IntegerField(blank=True,null=True)
    alv = models.DecimalField(max_digits=5,blank=True,null=True, default = 72,decimal_places=2)
    category = models.CharField(max_length=50,blank=True,null=True)
    alvrange = models.CharField(max_length=50,blank=True,null=True)
    resguarentee = models.CharField(max_length=50,blank=True,null=True)
    reserverules = models.CharField(max_length=50,blank=True,null=True)
    extraday = models.BooleanField(blank=True,null=True,default=False)
    airline = models.ForeignKey(AirlineList,default ='', max_length=100,on_delete=models.SET_DEFAULT,blank=True, null=True)
    rll = models.IntegerField(blank=True,null=True)

    
    def __str__(self):
        return self.calendarmonth,self.bidperiodstart,self.bidperiodend,self.alv




    
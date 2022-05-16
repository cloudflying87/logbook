from re import T
from django.db import models
from datetime import datetime
from django import utils

class Engine(models.Model):
    engcode = models.IntegerField(primary_key=True, null=False,default = '0')
    mfr = models.CharField(max_length=100, null=False)
    model = models.CharField(max_length=100, null=False)
    type = models.IntegerField(null=False)
    horsepower = models.IntegerField(blank=True,null=True)
    thrust = models.IntegerField(blank=True,null=True)
    date_added = models.DateTimeField(blank=True)
    date_edited = models.DateTimeField(blank=True)
    def __str__(self):
        return self.model

class Aircraftref(models.Model):
    mfrcode = models.CharField(primary_key=True, null=False,default = '0', max_length=20)
    mfr = models.CharField(max_length=100, null=False)
    model = models.CharField(max_length=100, null=False)
    typeacft = models.IntegerField(null=False)
    typeengine = models.IntegerField(null=False)
    accat = models.DecimalField(max_digits=5,decimal_places=1,null=False)
    buildcertid = models.IntegerField(null=False)
    numberengines = models.IntegerField(null=False)
    numberseats = models.IntegerField(null=False)
    acweight = models.CharField(max_length=100, null=False)
    speed = models.IntegerField(null=False)
    date_added = models.DateTimeField(blank=True)
    date_edited = models.DateTimeField(blank=True)
    def __str__(self):
        return self.model



class Master(models.Model):
    nnumber = models.CharField(primary_key=True, max_length=50, null=False,default = '0')
    serialnumber = models.CharField(null=True, blank=True, max_length=200)
    mfrcode = models.ForeignKey(Aircraftref, default = 12345678, on_delete=models.SET_DEFAULT)
    engcode = models.ForeignKey(Engine, default = 12345678, on_delete=models.SET_DEFAULT)
    airworthdate = models.IntegerField(null=True, blank=True)
    yearmfr = models.IntegerField(null=True, blank=True)
    date_added = models.DateTimeField(blank=True, null=True, default=utils.timezone.now)
    date_edited = models.DateTimeField(blank=True, null=True, default=utils.timezone.now)
    def __str__(self):
        return self.nnumber

class Manufacture(models.Model):
    manufacture = models.CharField(max_length=100, null=False)
    date_added = models.DateTimeField(blank=True)
    date_edited = models.DateTimeField(blank=True)
    def __str__(self):
        return self.manufacture
class AircraftModel(models.Model):
    type = models.CharField(primary_key=True, null=False,default = '0', max_length=20)
    mfr = models.ForeignKey(Manufacture, default = 12345678, on_delete=models.SET_DEFAULT)
    numberengines = models.IntegerField(null=False, default=1)
    land = models.BooleanField(default=True)
    sea = models.BooleanField(default=False)
    tailwheel = models.BooleanField(default=False)
    turboprop = models.BooleanField(default=False)
    complex = models.BooleanField(default=False)
    highperformance = models.BooleanField(default=False)
    turbofan = models.BooleanField(default=False)
    turbine = models.BooleanField(default=False)
    rotorcraft = models.BooleanField(default=False)
    poweredlift = models.BooleanField(default=False)
    numberseats = models.IntegerField(null=True,blank=True)
    acweight = models.CharField(max_length=100, null=True,blank=True)
    date_added = models.DateTimeField(blank=True)
    date_edited = models.DateTimeField(blank=True)
    def __str__(self):
        return self.type
class NewPlaneMaster(models.Model):
    nnumber = models.CharField(primary_key=True, max_length=50, null=False,default = '0')
    taa = models.BooleanField
    aircraftmodel = models.ForeignKey(AircraftModel, default = 12345678, on_delete=models.SET_DEFAULT)
    date_added = models.DateTimeField(blank=True, null=True, default=utils.timezone.now)
    date_edited = models.DateTimeField(blank=True, null=True, default=utils.timezone.now)
    def __str__(self):
        return self.nnumber


from django.db import models
from datetime import datetime

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
    mfrcode = models.ForeignKey(Aircraftref, default = 'none', on_delete=models.SET_DEFAULT)
    engcode = models.ForeignKey(Engine, default = 'none', on_delete=models.SET_DEFAULT)
    airworthdate = models.IntegerField(null=True, blank=True)
    yearmfr = models.IntegerField(null=True, blank=True)
    date_added = models.DateTimeField(blank=True, null=True, default=datetime.now())
    date_edited = models.DateTimeField(blank=True, null=True, default=datetime.now())
    def __str__(self):
        return self.nnumber
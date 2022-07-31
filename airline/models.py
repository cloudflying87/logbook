from unittest.util import _MAX_LENGTH
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

class AirlineSchedule(models.Model):
    importdate = models.DateField(default=utils.timezone.now)
    rotationnumber = models.CharField(max_length=4,null=True,blank=True)
    airline = models.ForeignKey(AirlineList,default ='', max_length=100,on_delete=models.SET_DEFAULT)
    rawdata = tinymce_models.HTMLField()
    def __str__(self):
        return self.rotationnumber
    
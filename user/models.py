from typing import Text
from django.db import models


class Users(models.Model):
    user_id = models.IntegerField(blank=True,null=True)
    pic = models.BooleanField(blank=True,null=True)
    sic = models.BooleanField(blank=True,null=True)
    cfi = models.BooleanField(blank=True,null=True)
    dual = models.BooleanField(blank=True,null=True)
    solo = models.BooleanField(blank=True,null=True)
    defaultairport = models.CharField(max_length=10,blank=True,null=True)
    defaultairplane = models.CharField(max_length=10,blank=True,null=True)
    airlineform = models.BooleanField(blank=True,null=True)
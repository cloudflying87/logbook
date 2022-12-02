from django.db import models
from aircraft.models import AircraftModel, NewPlaneMaster
from airport.models import Airport
from django import utils
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django_currentuser.middleware import (
    get_current_user)


class FlightTime(models.Model):
    userid= models.IntegerField()
    flightdate = models.DateField(default=utils.timezone.now)
    aircraftId = models.ForeignKey(NewPlaneMaster,default='N1234DLH',on_delete=models.SET_DEFAULT)
    departure = models.CharField(max_length=4,blank=True,null=True)
    route = models.CharField(max_length=100,blank=True,null=True)
    arrival = models.CharField(max_length=4,blank=True,null=True)
    flightnum = models.IntegerField(blank=True,null=True)
    deptime = models.TimeField(blank=True,null=True)
    offtime = models.TimeField(blank=True,null=True)
    ontime = models.TimeField(blank=True,null=True)
    arrtime = models.TimeField(blank=True,null=True)
    landings = models.IntegerField(blank=True,null=True)
    imc = models.DecimalField(max_digits=5, blank=True,null=True, decimal_places=2)
    hood = models.DecimalField(max_digits=5, blank=True,null=True, decimal_places=2)
    iap = models.IntegerField(blank=True,null=True)
    typeofapproach = models.CharField(max_length=10,blank=True,null=True)
    descriptionofapproach = models.CharField(max_length=100,blank=True,null=True)
    holdnumber = models.IntegerField(blank=True,null=True)
    holdboolean = models.BooleanField(blank=True,null=True)
    pic = models.DecimalField(max_digits=5, blank=True,null=True, decimal_places=2)
    sic = models.DecimalField(max_digits=5, blank=True,null=True, decimal_places=2)
    cfi = models.DecimalField(max_digits=5, blank=True,null=True, decimal_places=2)
    dual = models.DecimalField(max_digits=5, blank=True,null=True, decimal_places=2)
    crosscountry = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True) 
    solo = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    total = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    day = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    daylandings = models.IntegerField(blank=True,null=True)
    night = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    nightlandings = models.IntegerField(blank=True,null=True)
    printcomments = models.CharField(max_length=1000, blank=True)
    personalcomments = models.CharField(max_length=300, blank=True)
    ftd = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    ftdimc = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    sim = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    simimc = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    pcatd = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    pcimc = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    instructor = models.CharField(max_length=45, blank=True)   
    instructorid = models.IntegerField(blank=True,null=True,default=0)
    student = models.CharField(max_length=50, blank=True)
    studentid= models.IntegerField(blank=True,null=True,default=0)
    captain = models.CharField(max_length=50, blank=True)
    firstofficer = models.CharField(max_length=50, blank=True)
    flightattendants = models.CharField(max_length=50, blank=True)
    passengercount = models.IntegerField(blank=True,null=True)
    scheduleddeparttime = models.TimeField(blank=True,null=True)
    scheduledarrivaltime = models.TimeField(blank=True,null=True)
    scheduledblock = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    rotationid = models.CharField(max_length=50,blank=True,null=True)
    aircrafttype = models.ForeignKey(AircraftModel,default ='B737-900',on_delete=models.SET_DEFAULT)
    flighttime = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    distance = models.IntegerField(blank=True,null=True)
    scheduleddeparttimelocal = models.TimeField(blank=True,null=True)
    scheduledarrivaltimelocal = models.TimeField(blank=True,null=True)
    deptimelocal = models.TimeField(blank=True,null=True)
    offtimelocal = models.TimeField(blank=True,null=True)
    ontimelocal= models.TimeField(blank=True,null=True)
    arrtimelocal = models.TimeField(blank=True,null=True)
    reporttime = models.TimeField(blank=True,null=True)
    reporttimelocal = models.TimeField(blank=True,null=True)
    minutesunder = models.DecimalField(max_digits=5, blank=True, decimal_places=2,null=True)
    flightupdated = models.DateTimeField(blank=True,null=True)
    flightcreated = models.DateTimeField(blank=True,null=True)
    domestic = models.BooleanField(blank=True,null=True)
    international = models.BooleanField(blank=True,null=True)
    paycode = models.CharField(max_length=50,blank=True,null=True)
    scheduledflight = models.BooleanField(blank=True,null=True)
    deadheadflight = models.BooleanField(blank=True,null=True)
    startdate = models.DateTimeField(blank=True,null=True)
    departuregate = models.CharField(max_length=50,blank=True,null=True)
    arrivalgate = models.CharField(max_length=50,blank=True,null=True)
    flightpath = models.CharField(max_length=50,blank=True,null=True)
    airspeed = models.IntegerField(blank=True,null=True)
    filedalt = models.IntegerField(blank=True,null=True)

    def __str__(self):
        return '{} {} {} {} {}'.format(self.flightdate,self.departure,self.arrival,self.aircraftId,self.personalcomments)

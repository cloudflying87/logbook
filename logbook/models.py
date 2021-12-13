from django.db import models
from aircraft.models import Master,Aircraftref


class FlightTime(models.Model):
    userid= models.IntegerField()
    flightdate = models.DateField()
    aircraftId = models.ForeignKey(Master,default='N1234DLH',on_delete=models.SET_DEFAULT)
    departure = models.CharField(default ='', max_length=100,blank=True,null=True)
    route = models.CharField(max_length=100,blank=True,null=True)
    arrival = models.CharField(default ='', max_length=100,blank=True,null=True)
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
    instructorid = models.IntegerField(blank=True,null=True)
    student = models.CharField(max_length=50, blank=True)
    studentid= models.IntegerField(blank=True,null=True)
    captain = models.CharField(max_length=50, blank=True)
    firstofficer = models.CharField(max_length=50, blank=True)
    flightattendants = models.CharField(max_length=50, blank=True)
    passengercount = models.IntegerField(blank=True,null=True)
    scheduleddeparttime = models.TimeField(blank=True,null=True)
    scheduledarrivaltime = models.TimeField(blank=True,null=True)
    typeacft = models.ForeignKey(Aircraftref, default=123456789, on_delete=models.SET_DEFAULT)
    typeengine = models.IntegerField(null=True)
    numberengines = models.IntegerField(null=True)
    scheduledflight = models.BooleanField(blank=True,null=True)
    
    

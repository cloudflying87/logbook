from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django_currentuser.middleware import (
    get_current_user)
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from numpy import sort
from airport.views import gettingairport,suntime
from aircraft.models import NewPlaneMaster
import time
from airport.models import Airport
from django.urls import reverse_lazy
from dal import autocomplete
from .forms import FlightTimeEntry
from datetime import datetime

class AirportAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Airport.objects.all().order_by('icao')
        if self.q:
            qs = qs.filter(icao__istartswith=self.q)
        return qs

class AircraftIDLookup(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = NewPlaneMaster.objects.all().order_by('nnumber')
        if self.q:
            qs = qs.filter(nnumber__istartswith=self.q)
        return qs

@login_required(login_url='/')
def logbookhome(request):
    print('hello')

def calculatetimes(time1,time2):
    #used to calculate times by subtracting time2 from time1 can be used for block time as well as flight time
    deptime = datetime.strptime(time1, '%H:%M')
    arrtime = datetime.strptime(time2, '%H:%M')
    duration = str(arrtime-deptime)
    if ',' in duration:
        daysplit = duration.split(',')
        (h,m,s) = daysplit[1].split(':')
    else:
        (h,m,s) = duration.split(':')
    durationdecimal = round(int(h)+(int(m)/60),2)
    print(durationdecimal)
    return durationdecimal

def gettingairportinfo(airportcode,unixtime,date):
    airportinfo = gettingairport(airportcode,unixtime)
    sunsettimes = suntime(airportcode,unixtime,date)
    
    
class LogbookEntry(FormView):
    
    template_name = 'logbook/main.html'
    form_class = FlightTimeEntry
    success_url = 'entry'

    
    def form_valid(self,form):
        instance = form.save(commit=False)
        #getting date information setup to be used for all the searches
        flightdate = datetime.strptime(form['flightdate'].value(),'%Y-%m-%d')
        unixdate = time.mktime(flightdate.timetuple())
        if form['departure'].value() != '':
            depairport = form['departure'].value()
            depairportinfo = gettingairportinfo(depairport,unixdate,flightdate)
        
        #calculating block time
        if form['arrtime'].value() != "" and form['deptime'].value() != "":
            arrtime = form['arrtime'].value()
            deptime = form['deptime'].value()
            instance.total= calculatetimes(deptime,arrtime)

        print(instance)
        instance.save()
        return super().form_valid(form)

def testairport(request):
    passingtime = time.time()
    icao = "KMSP"
    gatheredinfo = gettingairport(icao,passingtime)
    
    return render(request, 'logbook/main.html', {'gatheredinfo':gatheredinfo})
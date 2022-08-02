from contextlib import nullcontext
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django_currentuser.middleware import (
    get_current_user)
from django.views.generic import FormView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from numpy import sort
from airport.views import gettingairport,suntime
from aircraft.models import NewPlaneMaster
import time
from airport.models import Airport
from .models import FlightTime
from geopy.distance import great_circle
from django.urls import reverse_lazy
from dal import autocomplete
from .forms import FlightTimeEntry
from datetime import datetime, timedelta
import time
from user.models import Users
from django.core.paginator import Paginator
from django.contrib.auth.models import User

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

class LogbookDisply(ListView):
    
    model = FlightTime
    paginate_by = 25
    context_object_name = "flight_list"
    template_name = 'logbook/logbook.html'
    
    

    def get_queryset(self, *args, **kwargs):
        currentuser = str(get_current_user())
        userid=User.objects.get(username=currentuser).pk
    
        logbookdisplay = FlightTime.objects.all().filter(userid=userid).order_by('-flightdate')
        return logbookdisplay
    

# def logbookdisply(request):
#     currentuser = str(get_current_user())
#     userid=User.objects.get(username=currentuser).pk
    
#     logbookdisplay = FlightTime.objects.all().filter(userid=userid).order_by('flightdate')
#     entries = Paginator(logbookdisplay,25)

#     # getting the desired page number from url
#     page_number = request.GET.get('page')
#     print(entries.num_pages)
#     # try:
#     page_obj = entries.get_page(page_number)  # returns the desired page object
#     # except PageNotAnInteger:
#     #     # if page_number is not an integer then assign the first page
#     #     page_obj = entries.page(1)
#     # except EmptyPage:
#     #     # if page is empty then return last page
#     #     page_obj = entries.page(entries.num_pages)
#     context = {'page_obj': page_obj}
#     # sending the page object to index.html
#     # return render(request, 'index.html', context)

#     return render(request,'logbook/logbook.html',{'logbookdisplay':page_obj}) 


def calculatetimes(time1,time2,decimalplaces,decimal):
    #used to calculate times by subtracting time2 from time1 can be used for block time as well as flight time
    deptime = datetime.strptime(time1, '%H:%M')
    arrtime = datetime.strptime(time2, '%H:%M')
    duration = str(arrtime-deptime)
    if ',' in duration:
        daysplit = duration.split(',')
        (h,m,s) = daysplit[1].split(':')
    else:
        (h,m,s) = duration.split(':')
    durationdecimal = round(int(h)+(int(m)/60),decimalplaces)
    return durationdecimal

def gettingairportinfo(airportcode,unixtime,date):
    airportinfo = gettingairport(airportcode,unixtime)
    sunsettimes = suntime(airportcode,unixtime,date)
    return airportinfo,sunsettimes
    
#making sure night time makes sense 
def checkdaynight(night,total,landing,landingtime):

    if night > total: 
        nighttime = total 
        daytime = None 

        if landing > 0: 
            nightlanding = landing 
            daylanding = None 

            return nighttime,daytime,nightlanding,daylanding 
        else:
            return nighttime,daytime

    else: 
        nighttime = night 
        daytime = total - night 

    if nighttime < .1: 
        nighttime = None 
        daytime = total 

        if landing > 0: 
            nightlanding = None 
            daylanding = landing 
            return nighttime,daytime,nightlanding,daylanding  
        else:
            return nighttime,daytime

    elif daytime < .1: 
        nighttime = total 
        daytime = None 
        if landing > 0: 
            nightlanding = landing 
            daylanding = None 

            return nighttime,daytime,nightlanding,daylanding 
        else:
            return nighttime,daytime

    else: 
        if landingtime == 'day': 
            if landing > 0: 
                nightlanding = None 
                daylanding = landing 
                return nighttime,daytime,nightlanding,daylanding
            else:
                return nighttime,daytime 

        if landingtime == 'night': 
            if landing > 0: 
                nightlanding = landing 
                daylanding = None 

                return nighttime,daytime,nightlanding,daylanding 
            else:
                return nighttime,daytime

 

def nighttime(totaltime,deptime,arrtime,depsunrise,depsunset,arrsunrise,arrsunset,landing):
    
    #all night time 
    if deptime > depsunset and deptime < depsunrise and arrtime > arrsunset and arrtime < arrsunrise: 
        
        nighttime = totaltime 
        daytime = None
        if landing > 0: 
            nightlanding = landing 
            daylanding = None
            return nighttime,daytime,nightlanding,daylanding     
        else:
            return nighttime,daytime

    #all day time 
    if deptime < depsunset and deptime > depsunrise and arrtime < arrsunset and arrtime > arrsunrise: 
        
        nighttime = None 
        daytime = totaltime 
        if landing > 0: 
            nightlanding = None 
            daylanding = landing 
            return nighttime,daytime,nightlanding,daylanding 
        else:
            return nighttime,daytime

    #departing at night landing during the day 
    if deptime < depsunset and arrtime < arrsunset: 
        
        nightcalc = (depsunrise - deptime)
        nighttime = ((nightcalc.total_seconds())/60)/60
        
        landingtime = 'day' 
        check = checkdaynight(nighttime,totaltime,landing,landingtime) 
        return check
    #departing during the day landing at night 
    if deptime < depsunset and arrtime > arrsunset: 
        
        nightcalc = arrtime - arrsunset 
        nighttime = ((nightcalc.total_seconds())/60)/60
        landingtime = 'night' 
        check = checkdaynight(nighttime,totaltime,landing,landingtime) 
        return check
class LogbookEntry(FormView):
    
    template_name = 'logbook/main.html'
    form_class = FlightTimeEntry
    success_url = 'logbookdisplay'

    
    def form_valid(self,form):
        instance = form.save(commit=False)
        currentuser = str(get_current_user())
        userid=User.objects.get(username=currentuser).pk
        preferences = Users.objects.filter(user_id=userid).values()
        
        #getting date information setup to be used for all the searches
        flightdate = datetime.strptime(form['flightdate'].value(),'%Y-%m-%d')
        unixdate = time.mktime(flightdate.timetuple())
        #Getting departure airport information
        if form['departure'].value() != '':
            depairport = form['departure'].value()
            depairportinfo = gettingairportinfo(depairport,unixdate,flightdate)
            
            
        #getting arrival airport information from form and for night time calculations and distance calculations
        if form['arrival'].value() != '':
            arrairport = form['arrival'].value()
            arrairportinfo = gettingairportinfo(arrairport,unixdate,flightdate)
        #Setting landings to correctly
        if form['landings'].value() != '':
            landings = instance.landings
        else:
            landings = 0
        #calculating block time
        if form['arrtime'].value() != "" and form['deptime'].value() != "":
            arrtime = form['arrtime'].value()
            deptime = form['deptime'].value()
            decimalplaces = preferences[0]['decimalplaces']
            #setup for future development of hh:ss instead of decimal. 
            decimal=preferences[0]['decimal']
            total= calculatetimes(deptime,arrtime,decimalplaces,decimal)
            #Setting all the values based on user preferences, these times are set to autolog
            if preferences[0]['pic']:
                instance.pic = total
            if preferences[0]['sic']:
                instance.sic = total
            if preferences[0]['cfi']:
                instance.cfi = total
            if preferences[0]['dual']:
                instance.dual = total
            if preferences[0]['solo']:
                instance.solo = total
            instance.total= total
            # used to make sure that there is a departure airport and arrival airport before continuing with any of the calculations
            if form['departure'].value() != '' and form['arrival'].value() != '':
                #verfying the user preference is to autolog cross country time
                if preferences[0]['cx']:
                    #caculating distance between departure and arrival airports and then adding it to the instance
                    if (great_circle((depairportinfo[0]['airport']['lat'],depairportinfo[0]['airport']['long']),(arrairportinfo[0]['airport']['lat'],arrairportinfo[0]['airport']['long'])).nm) > 50:
                        instance.crosscountry = total
                #getting the times all set correctly to work on the night time calculations
                departuretime = datetime.combine(flightdate,datetime.strptime(deptime,'%H:%M').time())
                #Adding a day if we go to the next UTC day. 
                arrivaltime = datetime.combine(flightdate,datetime.strptime(arrtime,'%H:%M').time())
                if arrivaltime.time() < departuretime.time():
                    correctedarrivaltime = arrivaltime + timedelta(days=1)
                else:
                    correctedarrivaltime = arrivaltime

                nightcalc = nighttime(total,departuretime,correctedarrivaltime,depairportinfo[1]['sunriseUTC'],depairportinfo[1]['sunsetUTC'],arrairportinfo[1]['sunriseUTC'],arrairportinfo[1]['sunsetUTC'],landings)
                
                
                instance.night = nightcalc[0]
                instance.day = nightcalc[1]
                if landings > 0:
                    instance.nightlandings = nightcalc[2]
                    instance.daylandings = nightcalc[3]
        
        instance.save()
        return super().form_valid(form)

def testairport(request):
    passingtime = time.time()
    icao = "KMSP"
    gatheredinfo = gettingairport(icao,passingtime)
    
    return render(request, 'logbook/main.html', {'gatheredinfo':gatheredinfo})
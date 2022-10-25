import csv
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django_currentuser.middleware import (
    get_current_user)
from django.views.generic import FormView, DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView
from airport.views import gettingairport,suntime
from aircraft.models import NewPlaneMaster,AircraftModel
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
from user.views import getuserid

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
    #used to show all flights in the database for the user
    model = FlightTime
    paginate_by = 35
    context_object_name = "flight_list"
    template_name = 'logbook/logbook.html'
    

    def get_queryset(self, *args, **kwargs):
        logbookdisplay = FlightTime.objects.all().filter(userid=getuserid()).exclude(scheduledflight=True).order_by('-flightdate','scheduleddeparttime')
        return logbookdisplay

def converttoUTC(time,timezone):
    #converting local times to utc returns a string
    
    timeobject = datetime.strptime(time, '%H:%M')
    if timezone < 0:
        timecorrection = timeobject + timedelta(hours=abs(timezone))
        
    if timezone > 0:
        timecorrection = timeobject - timedelta(hours=abs(timezone))

    if timezone ==0:
        timecorrection = timeobject

    timecorrectionstring = timecorrection.strftime("%H:%M")
    
    return timecorrectionstring
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

def getextrasuntimes(airportcode,date):
    flightdate = date - timedelta(days=1)
    unixdate = time.mktime(flightdate.timetuple())
    suntimes = suntime(airportcode,unixdate,flightdate)
    previoussunset = suntimes['sunsetUTC']
    flightdate = date + timedelta(days=1)
    unixdate = time.mktime(flightdate.timetuple())
    suntimes = suntime(airportcode,unixdate,flightdate)
    nextsunrise = suntimes['sunriseUTC']

    return [previoussunset,nextsunrise]
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

def fixtime(timetofix):
    # Dealing with the :00 that are added with the form edit. 
    if len(timetofix) == 8:
        fixedtime = timetofix[:5]
    else:
        fixedtime = timetofix

    return fixedtime
 
def addingtimeanddate(flightdate,starttime,utcoffset):
    if datetime.strptime(starttime,'%H:%M').time() <= (datetime.strptime('23:59','%H:%M') - timedelta(hours=utcoffset)).time():
        zuludate = flightdate+ timedelta(days=1)
    else:
        zuludate = flightdate
    fixeddatetime = datetime.combine(zuludate,datetime.strptime(starttime,'%H:%M').time())
    
    return fixeddatetime

def nighttime(totaltime,deptime,arrtime,depsunsetp,depsunrise,depsunset,depsunrisen,arrsunsetp,arrsunrise,arrsunset,arrsunrisen,landing):
    
    formula = ''
    #all night time 
    if (deptime > depsunset and deptime < depsunrisen and arrtime > arrsunset and arrtime < arrsunrisen) or (deptime > depsunsetp and deptime < depsunrise and arrtime > arrsunsetp and arrtime < arrsunrise): 
        formula = 'allnight'  
        nighttime = totaltime 
        daytime = None
        if landing > 0: 
            nightlanding = landing 
            daylanding = None
            return nighttime,daytime,nightlanding,daylanding     
        else:
            return nighttime,daytime

    #all day time 
    if deptime <= depsunset and deptime >= depsunrise and arrtime <= arrsunset and arrtime >= arrsunrise: 
        formula = 'daytime'
        nighttime = None 
        daytime = totaltime 
        if landing > 0: 
            nightlanding = None 
            daylanding = landing 
            return nighttime,daytime,nightlanding,daylanding 
        else:
            return nighttime,daytime

    #departing at night landing during the day 
    if deptime <= depsunrise and arrtime <= arrsunset: 
        formula = 'nighttoday'
        if (depsunrise - deptime) < (arrtime - arrsunrise):
            nightcalc = depsunrise - deptime
        else:
            nightcalc = arrtime - arrsunrise 
            

        nighttime = round((((nightcalc.total_seconds())/60)/60),2)
        
        landingtime = 'day' 
        check = checkdaynight(nighttime,totaltime,landing,landingtime) 
        return check

    #departing during the day landing at night 
    if deptime <= depsunset and arrtime >= arrsunset: 
        formula = 'daytonight'
        if (depsunset-deptime) < (arrsunset-arrtime):
            nightcalc = depsunset-deptime 
        else:
            nightcalc = arrtime - arrsunset
            
            

        nighttime = round((((nightcalc.total_seconds())/60)/60),2)
        
        landingtime = 'night' 
        check = checkdaynight(nighttime,totaltime,landing,landingtime)
        return check

    #late departure into the sunrise of the next day
    if deptime <= depsunrisen and arrtime >= arrsunrisen: 
        formula = 'latedeparture'
        nightcalc = (arrtime - arrsunrisen)
        nighttime = round((((nightcalc.total_seconds())/60)/60),2)
        
        landingtime = 'day' 
        check = checkdaynight(nighttime,totaltime,landing,landingtime) 
        
        return check

class LogbookEntry(FormView):
    
    template_name = 'logbook/main.html'
    form_class = FlightTimeEntry
    success_url = '/logbook'

    
    def form_valid(self,form):
        instance = form.save(commit=False)
        #doing all the work on the data to save the flight to the database
        currentuser = str(get_current_user())
        userid=User.objects.get(username=currentuser).pk
        preferences = Users.objects.filter(user_id=userid).values()
        aircraft_type = NewPlaneMaster.objects.filter(nnumber=instance.aircraftId).values()
        instance.aircrafttype = AircraftModel.objects.get(type=aircraft_type[0]['aircraftmodel_id'])
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
            print(form['arrtime'].value())
            arrtime = fixtime(form['arrtime'].value())
            deptime = fixtime(form['deptime'].value())

            decimalplaces = preferences[0]['decimalplaces']
            #setup for future development of hh:ss instead of decimal. 
            decimal=preferences[0]['decimal']

            if form['offtime'].value() != "" and form['ontime'].value() != "":
                offtime = fixtime(form['offtime'].value())
                ontime = fixtime(form['ontime'].value())

                instance.flighttime = calculatetimes(offtime,ontime,decimalplaces,decimal)

                if instance.scheduledflight == 1:
                    instance.scheduledflight = 0

            
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
                    distance = (great_circle((depairportinfo[0]['airport']['lat'],depairportinfo[0]['airport']['long']),(arrairportinfo[0]['airport']['lat'],arrairportinfo[0]['airport']['long'])).nm)
                    instance.distance = distance
                    if distance > 50:
                        instance.crosscountry = total
                #getting the times all set correctly to work on the night time calculations
                departuretime = addingtimeanddate(flightdate,deptime,depairportinfo[0]['gmt_offset_single'])
                
                #if departure date gets one added to it then automatically add it to the arrival date, else run the formula on arrival date separately
                
                if departuretime>(flightdate+timedelta(days=1)) :
                    arrivaltime = datetime.combine((flightdate + timedelta(days=1)),datetime.strptime(arrtime,'%H:%M').time())
                else:
                    arrivaltime = addingtimeanddate(flightdate,arrtime,arrairportinfo[0]['gmt_offset_single'])
                
                #getting the previous sunset and the nextday sunrise, so I will know the times for both nights
                extrasuntimesdep = getextrasuntimes(depairport,flightdate)
                extrasuntimesarr = getextrasuntimes(arrairport,flightdate)

                nightcalc = nighttime(total,departuretime,arrivaltime,extrasuntimesdep[0],depairportinfo[1]['sunriseUTC'],depairportinfo[1]['sunsetUTC'],extrasuntimesdep[1],extrasuntimesarr[0],arrairportinfo[1]['sunriseUTC'],arrairportinfo[1]['sunsetUTC'],extrasuntimesarr[1],landings)
                
                instance.night = nightcalc[0]
                instance.day = nightcalc[1]
                if landings > 0:
                    instance.nightlandings = nightcalc[2]
                    instance.daylandings = nightcalc[3]
        
        instance.save()
        return super().form_valid(form)

def reworktimes2(request):
    currentuser = str(get_current_user())
    userid=User.objects.get(username=currentuser).pk
    filename = 'lulogbook2'
    with open('./logbook/fixtures/'+filename+'.csv','r') as read_file:
        logbook = csv.reader(read_file)
        leg = []
        allentries = []
        for count,entry in enumerate(logbook):
            flightdatetotal = datetime.strptime(entry[0],'%Y-%m-%d')
            flightdate = flightdatetotal.date()
            unixdate = time.mktime(flightdate.timetuple())
            depairportinfo = gettingairportinfo(entry[2],unixdate,flightdate)
            
            arrairportinfo = gettingairportinfo(entry[3],unixdate,flightdate)
            
            if (arrairportinfo[0]['airport']) == 'missing' or depairportinfo[0]['airport'] == 'missing':
                entry1 = entry[0],entry[1],entry[2],entry[3]
                allentries.append(entry1)
            else:
                distance = int((great_circle((depairportinfo[0]['airport']['lat'],depairportinfo[0]['airport']['long']),(arrairportinfo[0]['airport']['lat'],arrairportinfo[0]['airport']['long'])).nm))

                entry1 = entry[0],entry[1],entry[2],entry[3],distance
                allentries.append(entry1)

    with open('./logbook/fixtures/'+filename+'print.csv','w') as outfile:
        write = csv.writer(outfile)
        write.writerows(allentries)
    
    html = "<html><body>Good to go. {%timenow%} </body></html>" 
    return HttpResponse(html)

def reworktimes(request):
    currentuser = str(get_current_user())
    userid=User.objects.get(username=currentuser).pk
    filename = 'airlinecurrent'
    preferences = Users.objects.filter(user_id=userid).values()
    with open('./logbook/fixtures/'+filename+'.csv','r') as read_file:
        logbook = csv.reader(read_file)
        leg = []
        allentries = []
        for count,entry in enumerate(logbook):
            if (count/500).is_integer():
                print('still working',count)
            flightdatetotal = datetime.strptime(entry[0],'%Y-%m-%d %H:%M:%S')
            # flightdatetotal = datetime.strptime(entry[0],'%m/%d/%Y %H:%M:%S')
            flightdate = flightdatetotal.date()
            unixdate = time.mktime(flightdate.timetuple())
            tailnumber = entry[1]
            depairportinfo = gettingairportinfo(entry[2],unixdate,flightdate)
            arrairportinfo = gettingairportinfo(entry[4],unixdate,flightdate)
            if entry[10] != '':
                landings = int(entry[10])
            else:
                landings = 0
            
            if entry[6] != "" and entry[9] != "":
                arrtime = entry[9][:5]
                deptime = entry[6][:5]
                if entry[22] =='local':
                    deptime = converttoUTC(deptime,depairportinfo[0]['gmt_offset_single'])
                    arrtime = converttoUTC(arrtime,arrairportinfo[0]['gmt_offset_single'])
                decimalplaces = preferences[0]['decimalplaces']
                #setup for future development of hh:ss instead of decimal. 
                decimal=preferences[0]['decimal']
                
                if entry[7] != "" and entry[8] != "":
                    offtime = entry[7][:5]
                    ontime = entry[8][:5]
                    if entry[22] =='local':
                        offtime = converttoUTC(offtime,depairportinfo[0]['gmt_offset_single'])
                        ontime = converttoUTC(ontime,arrairportinfo[0]['gmt_offset_single'])
                    flighttime = calculatetimes(offtime,ontime,decimalplaces,decimal)
                else:
                    offtime = None
                    ontime = None
                    flighttime = None

                
                total= calculatetimes(deptime,arrtime,decimalplaces,decimal)
                    #caculating distance between departure and arrival airports and then adding it to the instance
                distance = int((great_circle((depairportinfo[0]['airport']['lat'],depairportinfo[0]['airport']['long']),(arrairportinfo[0]['airport']['lat'],arrairportinfo[0]['airport']['long'])).nm))
                
                if distance > 50:
                    crosscountry = total
                if entry[16] == "Y":
                    pic = total
                    fo = entry[19]
                else:
                    pic = None
                    fo = None
                if entry[17] == "Y":
                    sic = total
                    cap = entry[19]
                else:
                    sic = None
                    cap = None
                #getting the times all set correctly to work on the night time calculations
                departuretime = addingtimeanddate(flightdate,deptime,depairportinfo[0]['gmt_offset_single'])
                
                #if departure date gets one added to it then automatically add it to the arrival date, else run the formula on arrival date separately
                if departuretime.date()>flightdate:
                    arrivaltime = datetime.combine((flightdate + timedelta(days=1)),datetime.strptime(arrtime,'%H:%M').time())
                else:
                    arrivaltime = addingtimeanddate(flightdate,arrtime,arrairportinfo[0]['gmt_offset_single'])
                
                #getting the previous sunset and the nextday sunrise, so I will know the times for both nights
                extrasuntimesdep = getextrasuntimes(entry[2],flightdate)
                extrasuntimesarr = getextrasuntimes(entry[4],flightdate)

                nightcalc = nighttime(total,departuretime,arrivaltime,extrasuntimesdep[0],depairportinfo[1]['sunriseUTC'],depairportinfo[1]['sunsetUTC'],extrasuntimesdep[1],extrasuntimesarr[0],arrairportinfo[1]['sunriseUTC'],arrairportinfo[1]['sunsetUTC'],extrasuntimesarr[1],landings)
                
                
                    
                # with open('./logbook/fixtures/check.csv','a') as outfile:
                #     write = csv.writer(outfile)
                #     problem = count,flightdate,total,entry[2],entry[4],'night',nightcalc[0],'day',nightcalc[1],'',departuretime,extrasuntimesdep[0],depairportinfo[1]['sunriseUTC'],depairportinfo[1]['sunsetUTC'],extrasuntimesdep[1],'',arrivaltime,extrasuntimesarr[0],arrairportinfo[1]['sunriseUTC'],arrairportinfo[1]['sunsetUTC'],extrasuntimesarr[1]
                #     write.writerow(problem) 
                
                night = nightcalc[0]
                day = nightcalc[1]
                if landings > 0:
                    nightlandings = nightcalc[2]
                    daylandings = nightcalc[3]
                else:
                    nightlandings = None
                    daylandings = None
                
            aircrafttype = NewPlaneMaster.objects.filter(nnumber=tailnumber).values()
            
                
            workingdata = {
            'userid' : 2,
            'flightdate' : flightdate,
            'aircraftId' : tailnumber,
            'departure' : entry[2],
            'route' : entry[3],
            'arrival' : entry[4],
            'flightnum' : entry[5],
            'deptime' : deptime,
            'arrtime' : arrtime,
            'landings' : landings,
            'imc' : entry[11],
            'hood' : entry[12],
            'iap' : entry[13],
            'holdnumber' : entry[14],
            'aircrafttype':aircrafttype[0]['aircraftmodel_id'],
            'solo' : '',
            'pic' : pic,
            'sic' : sic,
            'dual' : '',
            'cfi' : '',
            'crosscountry' : crosscountry,
            'part135':'',
            'total' : total,
            'day' : day,
            'daylandings' : daylandings,
            'night' : night,
            'nightlandings' : nightlandings,
            'printcomments' : entry[18],
            'instructor' : '',
            'captain' : cap,
            'firstofficer' : fo,
            'student' : '',
            'flightattendants' : entry[20],
            'ftd' : '',
            'ftdimc' : '',
            'sim' : '',
            'simimc' : '',
            'pcatd' : '',
            'pcimc' : '',
            'passengercount' : entry[21],
            'offtime':offtime,
            'ontime':ontime,
            'flighttime':flighttime,
            'distance':distance
            }
            keys = workingdata.keys()
            allentries.append(workingdata)
            crosscountry = 0
            leg=[]
        
            
        
    with open('./logbook/fixtures/'+filename+'print.csv','w') as outfile:
        write = csv.DictWriter(outfile,keys)
        write.writerows(allentries)
    timenow = datetime.now().strftime("%H:%M")
    html = "<html><body>Good to go. {%timenow%} </body></html>" 
    return HttpResponse(html)

class EditEntry(LogbookEntry,UpdateView):
    
    model = FlightTime
    form = FlightTimeEntry
    pk_url_kwarg = 'id'
    template_name = 'logbook/editflight.html'
    success_url = '/logbook'
    

    # def get_initial(self,**kwargs):
    #     context = super(EditEntry, self).get_initial()
    #     context['form'] = self.form_class(instance=self.request.user,initial={
    #             'departure': self.get_object().departure,
    #             'arrival': self.get_object().arrival,
    #     })
        
        
    #     initial = super(EditEntry, self).get_initial()
    #     try:
    #         departure = self.get_object().departure
    #         arrival = self.get_object().arrival
    #     except:
    #         pass
    #     else:
    #         initial['departure'] = departure
    #         initial['arrival'] = arrival
    #     return initial

class ViewEntry(DetailView):
    
    model = FlightTime
    pk_url_kwarg = 'id'
    context_object_name = "flight"
    template_name = 'logbook/detail.html'

class DeleteEntry(DeleteView):
    
    model = FlightTime
    pk_url_kwarg = 'id'
    context_object_name = "flight"
    template_name = 'logbook/confirmdelete.html'
    success_url = '/logbook'
   
    
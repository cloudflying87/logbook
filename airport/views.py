from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from .models import Airport, Timezone, Zone
from suntime import Sun, SunTimeException
import time, datetime

@login_required(login_url='/')
def airporthome(request):
    return render(request, 'airport/airport_main.html', {})

def gettingairport(icao,passingtime):
    #Master function for getting airports and time zone information from the database. 
    airport_searched = icao
    
    #handles the aiport object from the database
    if len(airport_searched) == 4:
        airport = Airport.objects.filter(icao=airport_searched).values('icao','iata','name','city','state','country','elevation','lat','long','zone_name_id')
    
    if len(airport_searched) == 3:
        airport = Airport.objects.filter(iata=airport_searched).values('icao','iata','name','city','state','country','elevation','lat','long','zone_name_id')

    if not airport:
        return 'missing'
    else:    
        
        #takes the zonename from the airport table and finds the correct zoneid
        zoneid = Zone.objects.filter(zone_name=airport[0]['zone_name_id']).values()

        #with the zoneid finds the correct entry in the zone table
        timezoneinfo = Timezone.objects.filter(zone_id=zoneid[0]['zone_id']).filter(time_start__lte=passingtime).order_by('time_start').reverse().values('abbreviation','gmt_offset','dst')[0]
        
        gmt_offset_single = int(timezoneinfo['gmt_offset']/60/60)
        
        if timezoneinfo['dst'] == '0':
            daylightsavings = 'No'
        else:
            daylightsavings = 'Yes'

        if airport is not None:
            return({'airport':airport[0],'timezoneinfo':timezoneinfo,'gmt_offset_single':gmt_offset_single, 'daylightsavings':daylightsavings})

def airporturl(request,icao):
    passingtime = time.time()
    gatheredinfo = gettingairport(icao,passingtime)

    if gatheredinfo == 'missing':
        messages.success(request,icao+" Not Found")
        return render(request, 'airport/airport_main.html', {})
    else:
        return render(request,'airport/airportsearch.html', {'airport':gatheredinfo['airport'],'timezoneinfo':gatheredinfo['timezoneinfo'],'gmt_offset_single':gatheredinfo['gmt_offset_single'], 'daylightsavings':gatheredinfo['daylightsavings']})


def searchairport(request):
    if request.method == "POST":
        airport_searched = request.POST['airport_searched']
        #Handles the blank form entry
        if airport_searched == '':
            messages.success(request,"You forgot to type in an airport")
            return render(request, 'airport/airport_main.html', {})
        
        passingtime = time.time()
        gatheredinfo = gettingairport(airport_searched,passingtime)

        #handles the aiport object from the database
        if gatheredinfo == 'missing':
            messages.success(request,airport_searched+" Not Found")
            return render(request, 'airport/airport_main.html', {})
        else:
            return render(request,'airport/airportsearch.html', {'airport':gatheredinfo['airport'],'timezoneinfo':gatheredinfo['timezoneinfo'],'gmt_offset_single':gatheredinfo['gmt_offset_single'], 'daylightsavings':gatheredinfo['daylightsavings']})

    else:
        return render(request, 'airport/airport_main.html', {})


def getsuntimes(date,latitude,longitude):
    sun = Sun(latitude, longitude)
    sunrise = sun.get_sunrise_time(date)
    sunset = sun.get_sunset_time(date)
    return {'sunrise':sunrise,'sunset':sunset}

def suntime(airport,unixtime,datesearched):
    airportinfo = gettingairport(airport,unixtime)
        
    lat = float(airportinfo['airport']['lat'])
    long = float(airportinfo['airport']['long'])
    srsttimes = getsuntimes(datesearched,lat,long)
    # sunriseUTC = srsttimes['sunrise']
    
    sunriseUTC = datetime.datetime.utcfromtimestamp(time.mktime(srsttimes['sunrise'].timetuple()))
    sunriseUTCUnix = time.mktime(srsttimes['sunrise'].timetuple())
    sunriseLocal = datetime.datetime.utcfromtimestamp(time.mktime(srsttimes['sunrise'].timetuple())+airportinfo['timezoneinfo']['gmt_offset']).strftime('%H:%M')

    if srsttimes['sunset'].time() < srsttimes['sunrise'].time():
        correctsunsetdate = srsttimes['sunset'] + datetime.timedelta(days=1)
    else:
        correctsunsetdate = srsttimes['sunset']
    # sunsetUTC = srsttimes['sunset']
    
    sunsetUTC = datetime.datetime.utcfromtimestamp(time.mktime(correctsunsetdate.timetuple()))
    sunsetUTCUnix = time.mktime(correctsunsetdate.timetuple())
    sunsetLocal = datetime.datetime.utcfromtimestamp(time.mktime(correctsunsetdate.timetuple())+airportinfo['timezoneinfo']['gmt_offset']).strftime('%H:%M')

    return({'sunriseUTC':sunriseUTC,'sunriseUTCUnix':sunriseUTCUnix,'sunriseLocal':sunriseLocal,'sunsetUTC':sunsetUTC,'sunsetUTCUnix':sunsetUTCUnix,'sunsetLocal':sunsetLocal})


def sunriseset(request):
    if request.method == "POST":
        airport_searched = request.POST['airport_searched']
        date_searched = request.POST.get('date_searched')
        datesplit = date_searched.split('-')
        dateform = datetime.date(int(datesplit[0]),int(datesplit[1]),int(datesplit[2]))
        
        #Handles the blank form entry
        if airport_searched == '' and date_searched == '':
            messages.success(request,"You forgot to type in an airport and a date")
            return render(request, 'airport/sunriseset.html', {})
        if airport_searched == '':
            messages.success(request,"You forgot to enter an airport")
            return render(request, 'airport/sunriseset.html', {})
        if date_searched == '':
            messages.success(request,"You forgot to enter a date")
            return render(request, 'airport/sunriseset.html', {})  
        
        unixtime = time.mktime(dateform.timetuple())
        suntimes = suntime(airport_searched,unixtime,dateform)
        
        return render(request, 'airport/sunriseset.html', {'sunrise':suntimes['sunriseLocal'],'sunset':suntimes['sunsetLocal']})
    else:
        return render(request, 'airport/sunriseset.html',{})
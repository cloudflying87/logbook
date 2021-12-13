from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import re
import datetime
import time
import airport
from airport.views import gettingairport

@login_required(login_url='/')
def airlinehome(request):
    return render(request, 'airline/schedule.html', {})

def preferences():
      
            # if line == 'Names':
            #     add = 'no'
            # if line == 'A':
            #     captain = 'add'
            # if add == 'no' and captain == 'add':
            #     captainname.append(line)
            # if line == 'REG' and fo == '':
            #     captain = ''
            #     trip.append(captainname)
            #     captainname = []
            #     fo = 'add'
            # if add == 'no' and fo == 'add':
            #     foname.append(line)
            # if line == 'REG' and captain == '':
            #     trip.append(foname)
            #     fo = ''
            #     foname = []
            #     add = 'yes'
    base = 'MSP'
    return base
# def returndate(currentyear,currentdate):

def workdeltschedule(request):
    if request.method =='POST':
        schedule = request.POST.get('schedule')
        month = []
        trip = []
        count = 0
        base = preferences()
        schedulesp = schedule.split()
        year = schedulesp[1]
        add = 'yes'
        for count,line in enumerate(schedulesp):
            if line == base:
                month.append(trip)
                trip = []
            if line == 'Layover':
                add = 'no'
            if re.match("[0-9][0-9][A-Z][a-z][a-z]",line):
                add = 'yes'
                currentdate = datetime.datetime.strptime(line[0:2]+' '+line[2:6]+' '+ year,"%d %b %Y")
              
            if add == 'yes' and line != base and line != 'to':
                if '-' in line:
                    dept = line.split('-')
                    trip.append(dept[0])
                    trip.append(dept[1])
                elif '#' in line: 
                    trip.append(currentdate)
                    trip.append(line[1:])
                else:
                    trip.append(line)
        month.append(trip)  
        monthfinal = []
        for trip in month:
            for count,leg in enumerate(trip):
                tripnumber = trip[0]
                
                if type(leg) == datetime.datetime:
                    unixtime = time.mktime(leg.timetuple())
                    flightnum = trip[count + 1]
                    
                    departairportinfo = gettingairport(trip[count + 2],unixtime)

                    departairport = departairportinfo['airport']['icao']

                    departuretime = time.mktime(
                        datetime.datetime.combine(leg,datetime.datetime.strptime(trip[count+4],"%H%M").time())
                        .timetuple())-departairportinfo['timezoneinfo']['gmt_offset']
                    
                    arrivalairportinfo = gettingairport(trip[count + 3],unixtime)
                    arrivalairport = arrivalairportinfo['airport']['icao']
                    arrivaltime = time.mktime(
                        datetime.datetime.combine(leg,datetime.datetime.strptime(trip[count+5],"%H%M").time())
                        .timetuple())-arrivalairportinfo['timezoneinfo']['gmt_offset']
                    legtotal = [leg,flightnum,departairport,arrivalairport,departuretime,arrivaltime,round(((arrivaltime-departuretime)/60/60),2),trip[count+6],tripnumber]
                    
                    monthfinal.append(legtotal)
                    
        for leg in monthfinal:
            print(leg)
        
        return render(request, 'airline/masterschedule.html', {'schedule':monthfinal})
    else:
        return render(request, 'airline/schedule.html', {})
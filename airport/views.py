from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from airport.models import Airport, Timezone, Zone
from suntime import Sun, SunTimeException
import time, datetime
from user.views import getuserid
from django.views.generic.base import TemplateView
from django.views.generic import FormView
from logbook.models import FlightTime
from reports.forms import DateSelector
from django.db.models import Count,Sum,Avg
from django.db.models.functions import Round
from django.db.models import Q
import csv
import os
import plotly.graph_objects as go
import plotly.offline as plot
import pandas as pd
from django.db.models import TextField
from django.db.models.functions import Concat


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

def getsuntimes(date,latitude,longitude):
    sun = Sun(latitude, longitude)
    sunrise = sun.get_sunrise_time(date)
    sunset = sun.get_sunset_time(date)
    return {'sunrise':sunrise,'sunset':sunset}

def suntime(airport,unixtime,datesearched):
    airportinfo = gettingairport(airport,unixtime)
    try:
        lat = float(airportinfo['airport']['lat'])
        long = float(airportinfo['airport']['long'])
    except:
        print(airportinfo)
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

def callingdatabasedates2(startdate,enddate,userid):
    if type(startdate) == str and type(enddate) == str:
        flights = FlightTime.objects.filter(userid=userid,flightdate__gt=startdate,flightdate__lt=enddate).exclude(scheduledflight=True,deadheadflight=True)
    if type(startdate) == bool and type(enddate) == bool:
            flights = FlightTime.objects.filter(userid=userid).exclude(scheduledflight=True,deadheadflight=True)
    if type(startdate) == str and type(enddate) == bool:
        flights = FlightTime.objects.filter(userid=userid,flightdate__gt=startdate).exclude(scheduledflight=True,deadheadflight=True)
    if type(startdate) == bool and type(enddate) == str:
        flights = FlightTime.objects.filter(userid=userid,flightdate__lt=enddate).exclude(scheduledflight=True,deadheadflight=True)

    return flights

masterlist = []
airportlist = []
class FlightMap(FormView):
    template_name = 'airport/airportmap.html'
    form_class = DateSelector
    success_url = '../airport/drawmap'

    
    def form_valid(self,form):
        userid = getuserid()
        if form['frombeginning'].value():
            startdate = True
        else:
            startdate = form['startdate'].value()

        if form['toend'].value():
            enddate = True
        else:
            enddate = form['enddate'].value()
        
        masterlist = []
        airportlist = []
        try:
            flights = callingdatabasedates2(startdate,enddate,userid)
        except:
            print('fail')
            return redirect('flightmap')
        
        if os.path.exists('./savedfiles/airports.csv'):
            os.remove('./savedfiles/airports.csv')
            

        headerList = ['icao','airport','city','state','lat','long']
        
        # open CSV file and assign header
        with open("./savedfiles/airports.csv", 'w') as file:
            dw = csv.DictWriter(file, delimiter=',', 
                                fieldnames=headerList)
            dw.writeheader()

        if os.path.exists('./savedfiles/map.csv'):
            os.remove('./savedfiles/map.csv')

        # assign header columns
        headerList = ['start_lat','start_lon','end_lat','end_lon','airport1','airport2']
        
        # open CSV file and assign header
        with open("./savedfiles/map.csv", 'w') as file:
            dw = csv.DictWriter(file, delimiter=',', 
                                fieldnames=headerList)
            dw.writeheader()
        print(type(flights))
        totals = flights.aggregate(
            airtotal = Sum('total'),
                    miletotal = Sum('distance'),
                    paxtotal = Sum('passengercount'),
                    flighttotal = Count('total'),
                    avgflight = Avg('total'),
                    avgdistance = Avg('distance'),
                    avgpax = Avg('passengercount')
            )
        print(totals)
        for flight in flights:
            write = False
            # for most airline flights or just different departure and arrival airports this will work
            if flight.scheduledflight == True:
                continue
            if flight.departure != flight.arrival and flight.departure != None and flight.arrival != None and (flight.route == None or flight.route == ''):
                test = writecsv(flight.departure,flight.arrival)
                
            if flight.route != None and flight.route != '' and flight.departure == flight.arrival:
                route = (flight.route).split('-')
                route.sort()
                if len(route) == 1:
                    test = writecsv(flight.departure,route[0])
                elif len(route) == 2:
                    test = writecsv(flight.departure,route[0])
                    test = writecsv(route[0],route[1])
                    test = writecsv(route[1],flight.arrival)
                elif len(route) == 3:
                    test = writecsv(flight.departure,route[0])
                    test = writecsv(route[0],route[1])
                    test = writecsv(route[1],route[2])
                    test = writecsv(route[2],flight.arrival)
                elif len(route) == 4:
                    test = writecsv(flight.departure,route[0])
                    test = writecsv(route[0],route[1])
                    test = writecsv(route[1],route[2])
                    test = writecsv(route[2],route[3])
                    test = writecsv(route[3],flight.arrival)
                elif len(route) == 5:
                    test = writecsv(flight.departure,route[0])
                    test = writecsv(route[0],route[1])
                    test = writecsv(route[1],route[2])
                    test = writecsv(route[2],route[3])
                    test = writecsv(route[3],route[4])
                    test = writecsv(route[4],flight.arrival)

            if flight.route != None and flight.route != '' and flight.departure != flight.arrival:
                route = (flight.route).split('-')
                route.sort()
                if len(route) == 1:
                    test = writecsv(flight.departure,route[0])
                    test = writecsv(route[0],flight.arrival)
                elif len(route) == 2:
                    test = writecsv(flight.departure,route[0])
                    test = writecsv(route[0],route[1])
                    test = writecsv(route[1],flight.arrival)
                elif len(route) == 3:
                    test = writecsv(flight.departure,route[0])
                    test = writecsv(route[0],route[1])
                    test = writecsv(route[1],route[2])
                    test = writecsv(route[2],flight.arrival)
        with open('./savedfiles/mapinfo.csv','w') as outfile:
                write = csv.writer(outfile)
                rowinfo = len(test[0]),len(test[1]),len(flights)
                write.writerow(rowinfo)
                # write.writerow(totals['airtotal'])
                # write.writerow(len(test[0]))
                # write.writerow(len(test[1]))
                # write.writerow(len(flights))

        print('unique city pairs',len(test[0]),'unique airports',len(test[1]))
        return super().form_valid(form)
        # return self.render_to_response({'total':form})

def writecsv(departure,arrival):
    citypair = [departure,arrival]
    # print('unique city pairs',len(masterlist),'unique airports',len(airportlist))
    passingtime = time.time()
    citypair.sort()
    if not citypair in masterlist:
        airport1 = gettingairport(citypair[0],passingtime)
        airport2 = gettingairport(citypair[1],passingtime)
        if airport1 != 'missing' and airport2 != 'missing':
            info = airport1['airport']['lat'],airport1['airport']['long'],airport2['airport']['lat'],airport2['airport']['long'],citypair[0],citypair[1]
            masterlist.append(citypair)
            with open('./savedfiles/map.csv','a') as outfile:
                write = csv.writer(outfile)
                write.writerow(info)
            if not citypair[0] in airportlist:
                airportinfo = airport1['airport']['icao'],airport1['airport']['name'],airport1['airport']['city'],airport1['airport']['state'],airport1['airport']['lat'],airport1['airport']['long']
                airportlist.append(citypair[0])
                with open('./savedfiles/airports.csv','a') as outfile:
                    write = csv.writer(outfile)
                    write.writerow(airportinfo)
            if not citypair[1] in airportlist:
                airportinfo = airport2['airport']['icao'],airport2['airport']['name'],airport2['airport']['city'],airport2['airport']['state'],airport2['airport']['lat'],airport2['airport']['long']
                airportlist.append(citypair[1])
                with open('./savedfiles/airports.csv','a') as outfile:
                    write = csv.writer(outfile)
                    write.writerow(airportinfo)
    return masterlist,airportlist
    
def drawmap(request):

    df_airports = pd.read_csv('./savedfiles/airports.csv')
    df_airports.head()

    df_flight_paths = pd.read_csv('./savedfiles/map.csv')
    df_flight_paths.head()

    fig = go.Figure()

    flight_paths = []
    for i in range(len(df_flight_paths)):
        fig.add_trace(
            go.Scattergeo(
                locationmode = 'USA-states',
                lon = [df_flight_paths['start_lon'][i], df_flight_paths['end_lon'][i]],
                lat = [df_flight_paths['start_lat'][i], df_flight_paths['end_lat'][i]],
                mode = 'lines',
                line = dict(width = 1,color = 'red'),
                # opacity = float(df_flight_paths['cnt'][i]) / float(df_flight_paths['cnt'].max()),
            )
        )
    
    fig.add_trace(go.Scattergeo(
        locationmode = 'USA-states',
        lon = df_airports['long'],
        lat = df_airports['lat'],
        hoverinfo = 'text',
        text = df_airports['airport']+' '+df_airports['icao'],
        mode = 'markers',
        marker = dict(
            size = 5,
            color = 'rgb(255, 0, 0)',
            line = dict(
                width = 3,
                color = 'rgba(68, 68, 68, 0)'
            )
        )))
    
    fig.update_layout(
        title_text = 'My Flights',
        showlegend = False,
        geo = dict(
            scope = 'north america',
            framewidth=2000,
            projection_type = 'azimuthal equal area',
            showland = True,
            # showframe=False,
            framecolor='rgb(0, 243, 0)',
            landcolor = 'rgb(243, 243, 243)',
            countrycolor = 'rgb(204, 204, 204)',
        ),
    )

    
    fightml = fig.to_html()
    return render(request,'airport/drawmap.html',{'flight':fightml})
class AirportLookup(TemplateView):
    template_name = 'reports/airportreport.html'
    
    def get(self, request, *args, **kwargs):
        
        airportcount = []
        pagetitle = "Airports"
        userid = getuserid()
        secondrequest = request.GET.get('lookup[id]')

        depart = FlightTime.objects.filter(Q(departure=secondrequest) | Q(arrival=secondrequest),userid=userid).exclude(Q(scheduledflight=1) | Q(total=0)).order_by('-flightdate')

        return self.render_to_response({'total':depart.count(),'depart':depart,"title":pagetitle})

class SearchAirport(TemplateView):
    template_name = 'airport/airportsearch.html'

    def get(self, request, *args, **kwargs):
        secondrequest = request.GET.get('lookup[id]')
        passingtime = time.time()
        gatheredinfo = gettingairport(secondrequest,passingtime)
        
        return self.render_to_response({'airport':gatheredinfo['airport'],'timezoneinfo':gatheredinfo['timezoneinfo'],'gmt_offset_single':gatheredinfo['gmt_offset_single'], 'daylightsavings':gatheredinfo['daylightsavings']})
from cmd import PROMPT
import sys
from calendar import month
import secrets
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from airport.models import Airport
from logbook.models import FlightTime
from aircraft.models import NewPlaneMaster
from django_currentuser.middleware import (
    get_current_user)
from user.models import Users
from django.contrib.auth.models import User
from logbook.views import calculatetimes, converttoUTC
from .forms import AirlineScheduleEntry
import datetime
from datetime import datetime,timedelta
import time
import airport
from airport.views import gettingairport
from django.views.generic import FormView,View,ListView
from airline.models import AirlineSchedule
import datetime
import os.path
import re
from google.auth.transport.requests import Request

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import google_auth_oauthlib
import googleapiclient.discovery
from googleapiclient.errors import HttpError
from django.views.generic.edit import UpdateView
from user.forms import UserPreferences
from user.views import getuserid

state = ''

@login_required(login_url='/')
def airlinehome(request):
    return render(request, 'airline/schedule.html', {})


CLIENT_SECRETS_FILE = './airline/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

#function to get the userid for the database query for preferences


#for the google auth to see the calendar information 
def CalAuthView(request):
    CLIENT_SECRETS_FILE = './airline/credentials.json'
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    API_SERVICE_NAME = 'calendar'
    API_VERSION = 'v3'
    
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secrets_file=CLIENT_SECRETS_FILE,
        scopes=SCOPES)
    
    if (len(sys.argv) >= 2 and sys.argv[1] == 'runserver'):
        flow.redirect_uri = 'http://localhost:8000/airline/oauth2callback/'
        
    else:
        flow.redirect_uri = 'https://logbook.flyhomemn.com/airline/oauth2callback/'
    auth_flow = cal_base()
    auth_url = auth_flow.get_authenticated_service()
    
    return redirect(auth_url)
#for the google auth to see the calendar information 
class cal_base:

    def get_authenticated_service(self):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            client_secrets_file=CLIENT_SECRETS_FILE,
            scopes=SCOPES)
        if (len(sys.argv) >= 2 and sys.argv[1] == 'runserver'):
            flow.redirect_uri = 'http://localhost:8000/airline/oauth2callback/'
            
        else:
            flow.redirect_uri = 'https://logbook.flyhomemn.com/airline/oauth2callback/'

        authorization_url, state = flow.authorization_url(access_type='offline')
        state = state
        return authorization_url

#for the google auth to see the calendar information 
class Oauth2CallbackView(View):
    def get(self, request, *args, **kwargs):
        user = Users.objects.get(user_id=getuserid())
        calid = user.calendarid
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES,state=state)
        if (len(sys.argv) >= 2 and sys.argv[1] == 'runserver'):
            flow.redirect_uri = 'http://localhost:8000/airline/oauth2callback/'
            if calid != None:
                redirecturi = 'http://localhost:8000/airline/import'
            else:
                redirecturi = 'http://localhost:8000/airline/google'
        else:
            flow.redirect_uri = 'https://logbook.flyhomemn.com/airline/oauth2callback/'
            if calid !=None:
                redirecturi = 'https://logbook.flyhomemn.com/airline/import'
            else:
                redirecturi = 'https://logbook.flyhomemn.com/airline/google'
        #save the google credentials to the database
        flow.fetch_token(code=self.request.GET.get('code'))
        credentials = flow.credentials
        user = Users.objects.get(user_id=getuserid())
        user.token = credentials.token
        user.refresh_token = credentials.refresh_token
        user.token_uri = credentials.token_uri
        user.client_id = credentials.client_id
        user.client_secret = credentials.client_secret
        user.scopes = credentials.scopes
        user.save()

        return redirect(redirecturi)

def setcalid(request,id):
    user = Users.objects.get(user_id=getuserid())
    user.calendarid = id
    user.save()
    
    return render(request, 'airline/schedule.html')
def getcredentialsfromdb():
    user = Users.objects.get(user_id=getuserid())
    calid = user.calendarid
    
    credentials = Credentials(
        token=user.token,
        refresh_token = user.refresh_token,
        token_uri = user.token_uri,
        client_id = user.client_id,
        client_secret= user.client_secret)
        # scopes = user.scopes)
    return(calid,credentials)
#once the authentecation is complete we come here. First get
#the calendarid if it is not already been choosen
#after the calendar id is choosen then 
#if calendar id is already set then it goes to retreiving the information
def workdeltschedulegoogle(request):
    credentials = getcredentialsfromdb()
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials[1])

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates   
    added = []
    count = 0
    page_token = None
        
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            count = count + 1
            numcal = {'id':calendar_list_entry['id'],'name':calendar_list_entry['summary']}
            added.append(numcal)
            page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    return render(request, 'airline/choosecal.html', {'added': added})

def importingevents(request):
        
    credentials = getcredentialsfromdb()
        
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials[1])
    # here is retreving calendar events and then working them correctly to get everything in the database. 
    now = datetime.datetime.today().replace(day=1).isoformat() +'Z'
    calendarId=credentials[0]
    page_token = None
    monthrotations = []
    global added, notadded
    added = []
    notadded = []
    while True:
        events = service.events().list(calendarId=calendarId, pageToken=page_token,timeMin=now).execute()
        for event in events['items']:
            summarysplit = event['summary'].split()
            tripnum = summarysplit[0]
            tripstarttime = event['start']['dateTime']
            tripyear = tripstarttime[:4]
            tripendtime = event['end']['dateTime']
            if len(summarysplit) > 2:
                overnights = summarysplit[1:-1]
                rotationsummary = tripnum,overnights,tripstarttime,tripendtime
            else:
                rotationsummary = tripnum
            monthrotations.append(rotationsummary)
            description = event['description']
            descriptionsplit = description.split("\n")

            for count,item in enumerate(descriptionsplit):
                
                if item !='':
                    if item[0:3] == 'Rpt':
                        reporttimeraw = item[5:9]
                        reporttime = reporttimeraw[:2]+':'+reporttimeraw[2:]
                        reporttimeswitch = True
                        flightdate = (item[-5:])
                    if item[:2] =="D ":
                        leg = item[2:]
                        legsplit = leg.split()
                        deadhead = True
                        fixingleg(tripyear,flightdate,reporttime,legsplit,tripnum,reporttimeswitch,deadhead)
                        reporttimeswitch = False
                    if item[:2] =="DL":
                        leg = item
                        legsplit = leg.split()
                        deadhead = False
                        fixingleg(tripyear,flightdate,reporttime,legsplit,tripnum,reporttimeswitch,deadhead)
                        reporttimeswitch = False
                         
        page_token = events.get('nextPageToken')
        if not page_token:
            break
    print(monthrotations)
    return render(request, 'airline/masterschedule.html', {'added': added,'notadded':notadded}) 

def fixingleg(tripyear,legdate,reporttime,leg,rotationid,reporttimeswitch,deadhead):
    #getting all of the retreived calendar information in the correct format and then saving it to the database. Done leg by leg. 
    # this currently works with google and the way micrew exports to google
    #calendar

    #this will not have the correct date for a trip that goes across new years day. But I am getting the year from the start of the trip
    flightdate = (datetime.datetime.strptime(tripyear+legdate,'%Y%d%b')).date()
    unixdate = time.mktime(flightdate.timetuple())
    flightnumber = leg[0][2:]
    airports = leg[1].split('-')
    times = leg[2].split('-')
    
    departairportinfo = gettingairport(airports[0],unixdate)
    departairport = departairportinfo['airport']['icao']
    arrivalairportinfo = gettingairport(airports[1],unixdate)
    arrivalairport = arrivalairportinfo['airport']['icao']
    
    # #correcting for plus or minus GMT
    departuretime = converttoUTC(times[0],departairportinfo['gmt_offset_single'])

    # keeping the correct timezone for the reporttime. 
    if reporttimeswitch:
        global reporttimeszone
        reporttimeszone = departairportinfo['gmt_offset_single']
    reporttimeutc = converttoUTC(reporttime,reporttimeszone)
    
    arrivaltime = converttoUTC(times[1],arrivalairportinfo['gmt_offset_single'])
    

    # #this will need to be updated by userpreferences
    preferences = Users.objects.filter(user_id=getuserid()).values()
    decimal=preferences[0]['decimal']
    decimalplaces = preferences[0]['decimalplaces']
    blocktime = calculatetimes(departuretime,arrivaltime,decimalplaces,decimal)

    leg = [flightdate.strftime("%m/%d/%Y"),flightnumber,departairport,arrivalairport,departuretime,arrivaltime,blocktime,rotationid]

    if not FlightTime.objects.filter(userid=getuserid(),flightdate=flightdate,flightnum=flightnumber,departure=departairport,arrival=arrivalairport,scheduleddeparttime=departuretime).exists():
        flighttime = FlightTime()
        flighttime.userid = getuserid()
        flighttime.aircraftId = NewPlaneMaster.objects.get(nnumber = 'N802DN')
        flighttime.flightdate = flightdate
        flighttime.flightnum = flightnumber
        flighttime.departure = departairport
        flighttime.arrival = arrivalairport
        flighttime.scheduleddeparttime = departuretime
        flighttime.scheduledarrivaltime = arrivaltime
        flighttime.scheduledblock = blocktime
        flighttime.rotationid = rotationid
        flighttime.scheduleddeparttimelocal = times[0]
        flighttime.scheduledarrivaltimelocal = times[1]
        flighttime.reporttime = reporttimeutc
        flighttime.reporttimelocal = reporttime
        flighttime.deadheadflight = deadhead
        
        flighttime.scheduledflight = True
        flighttime.save()

        added.append(leg)
    else:
        notadded.append(leg)
class DeltaScheduleEntry(ListView):
    
    model = FlightTime
    template_name = 'airline/schedule.html'
    context_object_name = "flight_list"

    def get_queryset(self, *args, **kwargs):
        logbookdisplay = FlightTime.objects.all().filter(userid=getuserid(),scheduledflight=True).order_by('flightdate','scheduleddeparttimelocal')
        return logbookdisplay
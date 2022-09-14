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
    print(now)
    print(datetime.datetime.utcnow().isoformat() + 'Z' )
    # now = datetime.datetime.utcnow().isoformat() + 'Z' 
    calendarId=credentials[0]
    page_token = None
    trip = []
    monthsum = []
    while True:
        events = service.events().list(calendarId=calendarId, pageToken=page_token,timeMin=now).execute()
        for event in events['items']:
            summary = re.sub(r'\n','',event['summary'])
            tripnum = summary[0:4]
            triptimes = summary[-11:]
            description = event['description']
            descriptionsplit = description.split()

            for count,item in enumerate(descriptionsplit):
                match = re.search("[0-3][0-9][A-Z][A-Z][A-Z]",item)
                if match:
                        flightdate = item
                if item[0:2] =="DL":
                    flightnum = item[2:7]
                    depart = descriptionsplit[count+1][:3]
                    arr = descriptionsplit[count+1][-3:]
                    deptime = descriptionsplit[count+2][:5]
                    arrtime = descriptionsplit[count+2][-5:]
                    leg = [flightdate,flightnum,depart,arr,deptime,arrtime,tripnum]
                    trip.append(leg)
                    leg=[]
            monthsum.append(trip)  
            trip=[]      
        page_token = events.get('nextPageToken')
        if not page_token:
            break

    schedulelist = modifiyingschedule(monthsum)
    
    return render(request, 'airline/masterschedule.html', {'added': schedulelist[0],'notadded':schedulelist[1]}) 


def modifiyingschedule(schedule):
    #getting all of the retreived calendar information ready to go to the database. 
    # this currently works with google and the way micrew exports to google
    #calendar
    added = []
    notadded = []
    for trip in schedule:
        for leg in trip:
            flightdate = (datetime.datetime.strptime(leg[0]+datetime.datetime.today().strftime("%Y"),'%d%b%Y')).date()
            unixdate = time.mktime(flightdate.timetuple())
            flightnumber = leg[1]
            departairportinfo = gettingairport(leg[2],unixdate)
            departairport = departairportinfo['airport']['icao']
            arrivalairportinfo = gettingairport(leg[3],unixdate)
            arrivalairport = arrivalairportinfo['airport']['icao']
            #correcting for plus or minus GMT
            departuretime = converttoUTC(leg[4],departairportinfo['gmt_offset_single'])
            
            arrivaltime = converttoUTC(leg[5],arrivalairportinfo['gmt_offset_single'])
            

            #this will need to be updated by userpreferences
            preferences = Users.objects.filter(user_id=getuserid()).values()
            decimal=preferences[0]['decimal']
            decimalplaces = preferences[0]['decimalplaces']
            blocktime = calculatetimes(departuretime,arrivaltime,decimalplaces,decimal)
            rotationid = leg[6]
            
            leg = [flightdate.strftime("%m/%d/%Y"),flightnumber,departairport,arrivalairport,departuretime,arrivaltime,blocktime,rotationid]

            if not FlightTime.objects.filter(userid=getuserid(),flightdate=flightdate,flightnum=flightnumber).exists():
                flighttime = FlightTime()
                flighttime.userid = getuserid()
                flighttime.aircraftId = NewPlaneMaster.objects.get(nnumber = 'N802DN')
                flighttime.flightdate = flightdate
                flighttime.flightnum = flightnumber
                flighttime.departure = Airport.objects.get(icao = departairport)
                flighttime.arrival = Airport.objects.get(icao = arrivalairport)
                flighttime.scheduleddeparttime = departuretime
                flighttime.scheduledarrivaltime = arrivaltime
                flighttime.scheduledblock = blocktime
                flighttime.rotationid = rotationid
                
                flighttime.scheduledflight = True
                flighttime.save()
    
                added.append(leg)
            else:
                notadded.append(leg)
                    
    return added,notadded
class DeltaScheduleEntry(ListView):
    
    model = FlightTime
    template_name = 'airline/schedule.html'
    context_object_name = "flight_list"

    def get_queryset(self, *args, **kwargs):
        logbookdisplay = FlightTime.objects.all().filter(userid=getuserid(),scheduledflight=True).order_by('flightdate')
        return logbookdisplay
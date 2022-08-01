
from calendar import month
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from airport.models import Airport
from logbook.models import FlightTime
from aircraft.models import NewPlaneMaster
from django_currentuser.middleware import (
    get_current_user)
from user.models import Users
from django.contrib.auth.models import User
from logbook.views import calculatetimes
from .forms import AirlineScheduleEntry
import datetime
from datetime import datetime,timedelta
import time
import airport
from airport.views import gettingairport
from django.views.generic import FormView
from airline.models import AirlineSchedule
import datetime
import os.path
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


@login_required(login_url='/')
def airlinehome(request):
    return render(request, 'airline/schedule.html', {})


def workdeltschedulegoogle(request):

    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './airline/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        calendarId='jb360v1bcsqt0m7cf7sja0i06g@group.calendar.google.com'
        page_token = None
        trip = []
        monthsum = []
        while True:
            events = service.events().list(calendarId='jb360v1bcsqt0m7cf7sja0i06g@group.calendar.google.com', pageToken=page_token,timeMin=now).execute()
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
            
                # schedule.append(description)
                
            page_token = events.get('nextPageToken')
            if not page_token:
                break
        

    except HttpError as error:
        print('An error occurred: %s' % error)

    schedulelist = modifiyingschedule(monthsum)

    return render(request, 'airline/masterschedule.html', {'schedule': schedulelist}) 

def modifiyingschedule(schedule):
    schedulelist = []
    currentuser = str(get_current_user())
    userid=User.objects.get(username=currentuser).pk
    for trip in schedule:
        for leg in trip:
            flightdate = (datetime.datetime.strptime(leg[0]+datetime.datetime.today().strftime("%Y"),'%d%b%Y')).date()
            unixdate = time.mktime(flightdate.timetuple())
            flightnumber = leg[1]
            departairportinfo = gettingairport(leg[2],unixdate)
            departairport = departairportinfo['airport']['icao']
            arrivalairportinfo = gettingairport(leg[3],unixdate)
            arrivalairport = arrivalairportinfo['airport']['icao']
            departuretime = (datetime.datetime.strptime(leg[4], '%H:%M') + timedelta(hours=departairportinfo['gmt_offset_single'])).time()
            # departuretime = departuretimestart.strftime('%H:%M') 
            arrivaltime = (datetime.datetime.strptime(leg[5], '%H:%M') + timedelta(hours=departairportinfo['gmt_offset_single'])).time()
            blocktime = calculatetimes(departuretime.strftime('%H:%M'),arrivaltime.strftime('%H:%M'),2,1)
            leg = [flightdate,flightnumber,departairport,arrivalairport,departuretime,arrivaltime,blocktime,leg[6]]
            schedulelist.append(leg)
            flighttime = FlightTime()
            flighttime.userid = userid
            flighttime.aircraftId = NewPlaneMaster.objects.get(nnumber = 'N917DU')
            flighttime.flightdate = flightdate
            flighttime.flightnum = flightnumber
            flighttime.departure = Airport.objects.get(icao = departairport)
            flighttime.arrival = Airport.objects.get(icao = arrivalairport)
            # flighttime.arrival = arrivalairport
            flighttime.scheduleddeparttime = departuretime
            flighttime.scheduledarrivaltime = arrivaltime
            flighttime.scheduledblock = blocktime
            flighttime.rotationid = leg[6]
            flighttime.scheduledflight = True
            flighttime.save()

    
    
    return schedulelist
class DeltaScheduleEntry(FormView):
    
    template_name = 'airline/schedule.html'
    form_class = AirlineScheduleEntry
    success_url = '/airline'

    
    def form_valid(self,form):
        linebyline = []
        lines = []
        instance = form.save(commit=False)
        rawtrip = form['rawdata'].value()
        schedulesp = rawtrip.split()
        # print(schedulesp)
        for count,line in enumerate(schedulesp):
            if line == '<br':
                print(lines)
                linebyline.append(lines)
                lines = []
            
            else:
                lines.append(line)
        
        return render('airline/editschedule.html', {'schedule':schedulesp})


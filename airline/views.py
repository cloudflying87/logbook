from PyPDF2 import PdfReader
from cmd import PROMPT
import sys
from calendar import month
import secrets
from xml import dom
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from airport.models import Airport
from logbook.models import FlightTime
from aircraft.models import NewPlaneMaster
from django_currentuser.middleware import (
    get_current_user)
from user.models import Users
from django.contrib.auth.models import User
from logbook.views import calculatetimes, converttoUTC,addingtimeanddate, converttimetodecimal
from .forms import AirlineScheduleEntry
import datetime
from datetime import datetime,timedelta
import time
import airport
from airport.views import gettingairport
from django.views.generic import TemplateView,View,ListView, FormView
from airline.models import Rotations
from reports.forms import DateSelector
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
import requests
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from logbook.views import converttoUTC,calculatetimes

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

def workingisotime(object):
    #taking the ISO time object from google and converting it to python datetime object in zulutime
    objectsplit = object.split('T')
    if objectsplit[1][-1] == 'Z':
        datetodatetime = datetime.datetime.strptime(objectsplit[0],'%Y-%m-%d')
        convertedtime = objectsplit[1][:5]
        dateandtimeUTC = datetime.datetime.strptime(objectsplit[0]+' '+convertedtime,'%Y-%m-%d %H:%M')
    else:  
        #using the - sign to split, but that is actually indicating the gmt offset. works for me, but wouldnt work for plus gmt
        time = objectsplit[1][:5]
        timezone = objectsplit[1][8:11]
        convertedtime = converttoUTC(time,int(timezone))
        datetodatetime = datetime.datetime.strptime(objectsplit[0],'%Y-%m-%d')
        dateandtimeUTC = addingtimeanddate(datetodatetime,convertedtime,int(timezone))
    
    return [dateandtimeUTC,datetodatetime]
    
# class SelectDate(FormView):
#     template_name = 'airline/dateimport.html'
#     form_class = DateSelector
#     success_url = '/reports'
#     def get(self, request, *args, **kwargs):
#         pagetitle = "Export Reports"
#         return self.render_to_response({"title":pagetitle})

#     def post(self, request, *args, **kwargs):
#         userid=getuserid()
#         if 'startall' in request.POST:
#             startdate = True
#         else:
#             startdate = request.POST['startdate']
#         if 'endall' in request.POST:
#             enddate = True
#         else:
#             enddate = request.POST['enddate']
#         return 
  

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
        user_id=getuserid()
        preferences = Users.objects.get(user_id=user_id)
        
        airline = preferences.airline
        events = service.events().list(calendarId=calendarId, pageToken=page_token,timeMin=now).execute()
        
        for event in events['items']:
            #getting all the rotation information and saving it in the 
            #rotation table for pay calculations
            rotation = Rotations()
            tripcreated = workingisotime(event['created'])
            summarysplit = event['summary'].split()
            description = event['description']
            descriptionsplit = description.split("\n")
            tripnum = summarysplit[0]
            tripstarttime = event['start']['dateTime']
            tripyear = tripstarttime[:4]
            tripendtime = event['end']['dateTime']
            overnights=[]
            if len(summarysplit) > 2:
                overnightraw = summarysplit[1:-1]
                for summaryitem in overnightraw:
                    summaryitem = summaryitem.replace(',','')
                    overnights.append(summaryitem)
                #converting to correct datetime in zulu for start and endtimes
                tripstartzulu = workingisotime(tripstarttime)
                tripendzulu = workingisotime(tripendtime)
                tafb = round(((((tripendzulu[0]-tripstartzulu[0]).total_seconds())/60)/60),2)
                #does not include the 2am cutout. 
                tripdays = ((tripendzulu[1]-tripstartzulu[1]).days)+1
                rotation.userid = user_id
                rotation.rotationid = str(tripnum)
                rotation.rotationstart = tripstartzulu[0]
                rotation.rotationend = tripendzulu[0]
                rotation.googleimportdate = tripcreated[0]
                rotation.scheduledtafb = tafb
                rotation.days = tripdays
                rotation.rawdata = description
                rotation.overnights = str(overnights)
                rotation.logbookimportdate = datetime.datetime.now()
                rotation.airline = airline
                rotationsummary = type(user_id),type(tripnum),type(str(overnights)),tripstartzulu,tripendzulu,tripcreated,tafb,tripdays
            else:
                rotationsummary = tripnum
            # print(rotationsummary)
            
            for item in descriptionsplit:
                if item !='':
                    if item[0:3] == 'Rpt':
                        reporttimeraw = item[5:9]
                        reporttime = reporttimeraw[:2]+':'+reporttimeraw[2:]
                        reporttimeswitch = True
                        flightdate = (item[-5:])
                    if item[:2] =="D " or item[:2] =="O ":
                        leg = item[2:]
                        legsplit = leg.split()
                        deadhead = True
                        fixingleg(tripyear,flightdate,reporttime,legsplit,tripnum,reporttimeswitch,deadhead,tripstartzulu)
                        reporttimeswitch = False
                    if item[:2] =="DL":
                        leg = item
                        legsplit = leg.split()
                        deadhead = False
                        fixingleg(tripyear,flightdate,reporttime,legsplit,tripnum,reporttimeswitch,deadhead,tripstartzulu)
                        reporttimeswitch = False
                    if 'TL' and 'BL' and 'CR' in item:
                        timesplit = item.split()
                        rotation.rotationpay = converttimetodecimal(timesplit[0][:5])
                        rotation.rotationblock = converttimetodecimal(timesplit[1][:5])
                        rotation.rotationcredit = converttimetodecimal(timesplit[2][:5])
                    if item[:4] =="This":
                        eachword = item.split()
                        micrewexport = datetime.datetime.strptime(str(tripcreated[0].year)+'-'+eachword[4], '%Y-%d%b').date()
                        zulumicrew = converttoUTC(eachword[6],int(eachword[8][:3]))
                        combinedmicrew = addingtimeanddate(micrewexport,zulumicrew,int(eachword[8][:3]))
                        
                        rotation.micrewexportdate = combinedmicrew
            rotation.save()
                         
        page_token = events.get('nextPageToken')
        if not page_token:
            break
    
    return render(request, 'airline/masterschedule.html', {'added': added,'notadded':notadded}) 

def fixingleg(tripyear,legdate,reporttime,leg,rotationid,reporttimeswitch,deadhead,tripstart):
    #getting all of the retreived calendar information in the correct format and then saving it to the database. Done leg by leg. 
    # this currently works with google and the way micrew exports to google calendar via apple calendar

    #this will not have the correct date for a trip that goes across new years day. But I am getting the year from the start of the trip
    # This has problems with the day that Daylight savings switches
    userid = getuserid()
    flightdate = (datetime.datetime.strptime(tripyear+legdate,'%Y%d%b')).date()
    flightdatetime = (datetime.datetime.strptime(tripyear+legdate+reporttime,'%Y%d%b%H:%M'))

    unixdate = time.mktime(flightdatetime.timetuple())
    flightnumber = leg[0][2:]
    airports = leg[1].split('-')
    times = leg[2].split('-')
    
    departairportinfo = gettingairport(airports[0],unixdate)
    departairport = departairportinfo['airport']['icao']
    arrivalairportinfo = gettingairport(airports[1],unixdate)
    arrivalairport = arrivalairportinfo['airport']['icao']
    
    if departairportinfo['airport']['country'] != 'US' or arrivalairportinfo['airport']['country'] != 'US': 
        international = True
        domestic = False
    else: 
        international = False
        domestic = True
    #correcting for plus or minus GMT
    departuretime = converttoUTC(times[0],departairportinfo['gmt_offset_single'])

    # keeping the correct timezone for the reporttime. 
    if reporttimeswitch:
        global reporttimeszone
        reporttimeszone = departairportinfo['gmt_offset_single']
    reporttimeutc = converttoUTC(reporttime,reporttimeszone)
    
    arrivaltime = converttoUTC(times[1],arrivalairportinfo['gmt_offset_single'])
    

    # #this will need to be updated by userpreferences
    preferences = Users.objects.get(user_id=userid)
    decimal=preferences.decimal
    decimalplaces = preferences.decimalplaces
    blocktime = calculatetimes(departuretime,arrivaltime,decimalplaces,decimal)

    leg = [flightdate.strftime("%m/%d/%Y"),flightnumber,departairport,arrivalairport,departuretime,arrivaltime,blocktime,rotationid]
    #saving to the database
    if not FlightTime.objects.filter(userid=userid,flightdate=flightdate,flightnum=flightnumber,departure=departairport,arrival=arrivalairport,scheduleddeparttime=departuretime).exists():
        
        flighttime = FlightTime()
        flighttime.userid = userid
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
        flighttime.international = international
        flighttime.domestic = domestic
        flighttime.scheduledflight = True
        flighttime.startdate = tripstart
        flighttime.flightcreated = datetime.datetime.now()
        # flighttime.save()

        added.append(leg)
    else:
        notadded.append(leg)
class DeltaScheduleEntry(ListView):
    #for showing scheduled flights
    model = FlightTime
    template_name = 'airline/schedule.html'
    context_object_name = "flight_list"

    def get_queryset(self, *args, **kwargs):
        todaydate = datetime.datetime.now()
        scheduledflightdatecutoff = todaydate - timedelta(days=3)
        # print(scheduledflightdatecutoff)
        logbookdisplay = FlightTime.objects.all().filter(userid=getuserid(),scheduledflight=True,flightdate__gt=scheduledflightdatecutoff).order_by('flightdate','scheduleddeparttimelocal')
        return logbookdisplay

class SimpleUpload(TemplateView):
    template_name = 'airline/upload.html'

    def post(self,form):
        myfile = self.request.FILES['myfile']
        reader = PdfReader(myfile)
        number_of_pages = len(reader.pages)
        page = reader.pages[4]
        text = page.extract_text()
        print(number_of_pages,text)
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        # return render(request, 'core/simple_upload.html', {
        #     'uploaded_file_url': uploaded_file_url
        # })

def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        

        reader = PdfReader(myfile)
        number_of_pages = len(reader.pages)
        for pages in reader:
            page = reader.pages[pages]
            text = page.extract_text()
            print(text)
        fs = FileSystemStorage('/fixtures/BidPackage')
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'airline/upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'airline/upload.html')
class DeletemultipleQuery(ListView):
    
    model = FlightTime
    template_name = 'airline/deletemultiple.html'
    context_object_name = "flight_list"

    def get_queryset(self, *args, **kwargs):
        logbookdisplay = FlightTime.objects.all().filter(userid=getuserid(),scheduledflight=True).order_by('flightdate','scheduleddeparttimelocal')
        return logbookdisplay


class DeleteMultipleFlights(FormView):
    

    def get(self,form):
        print('valid')
        

def flightaware(ident,startdate,enddate):
        # ident = 'DAL2183'
        # startdate = '2022-10-09T17:59Z'
        # enddate = '2022-10-09T21:09Z'
        params = {"start":startdate,"end":enddate}
        endpoint = "https://aeroapi.flightaware.com/aeroapi/flights/{fident}"
        url = endpoint.format(fident=ident)
        
        headers = {'x-apikey': os.getenv('flightawareapi')}
        response = requests.get(url, params=params, headers=headers)
        
        endpoint = "https://aeroapi.flightaware.com/aeroapi/history/flights/{fident}"
        url = endpoint.format(fident=ident)
        
        headers = {'x-apikey': os.getenv('flightawareapi')}
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:  # SUCCESS
            result = response.json()
            
            if result['flights']:
                departairport = result['flights'][0]['origin']['code_icao']
                arrivalairport = result['flights'][0]['destination']['code_icao']
                flightnum = result['flights'][0]['ident_iata']
                tailnumber = result['flights'][0]['registration']
                scheduledout = result['flights'][0]['scheduled_out']
                if scheduledout != None:
                    scheduledout = changetonormaltime(scheduledout)
                actualout = result['flights'][0]['actual_out']
                if actualout != None:
                    actualout = changetonormaltime(actualout)
                scheduledoff = result['flights'][0]['scheduled_off']
                if scheduledoff != None:
                    scheduledoff = changetonormaltime(scheduledoff)
                actualoff = result['flights'][0]['actual_off']
                if actualoff != None:
                    actualoff = changetonormaltime(actualoff)
                scheduledon = result['flights'][0]['scheduled_on']
                if scheduledon != None:
                    scheduledon = changetonormaltime(scheduledon)
                actualon = result['flights'][0]['actual_on']
                if actualon != None:
                    actualon = changetonormaltime(actualon)
                scheduledin = result['flights'][0]['scheduled_in']
                if scheduledin != None:
                    scheduledin = changetonormaltime(scheduledin)
                actualin = result['flights'][0]['actual_in']
                if actualin != None:
                    actualin = changetonormaltime(actualin)
                departgate = result['flights'][0]['gate_origin']
                arrivalgate = result['flights'][0]['gate_destination']
                airspeed = result['flights'][0]['filed_airspeed']
                filedalt = result['flights'][0]['filed_altitude']
                route = result['flights'][0]['route']

                flight = {'departairport':departairport, 'arrivalairport':arrivalairport, 'tailnumber':tailnumber, 'flightnum':flightnum, 'scheduledout': scheduledout, 'actualout': actualout,'scheduledoff':scheduledoff,'actualoff':actualoff,'scheduledon':scheduledon,'actualon':actualon,'scheduledin':scheduledin,'actualin':actualin, 'departgate':departgate,'arrivalgate':arrivalgate,'airspeed':airspeed,'filedalt':filedalt,'route':route}
            else:
                flight = 'missing'
        else:
            flight = 'missing'
        
        return flight

def changetonormaltime(time):
    fixed = time[11:16]
    return fixed
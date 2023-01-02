from PyPDF2 import PdfReader
import csv
from decimal import Decimal
from cmd import PROMPT
import sys
from calendar import month
import secrets
from xml import dom
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from airport.models import Airport
from logbook.models import FlightTime
from aircraft.models import NewPlaneMaster,AircraftModel
from django_currentuser.middleware import (
    get_current_user)
from user.models import Users
from django.contrib.auth.models import User
from logbook.views import calculatetimes, converttoUTC,addingtimeanddate, converttimetodecimal,gettingairportinfo,converttolocal,nighttime,checkdaynight,getextrasuntimes
from geopy.distance import great_circle
from .forms import AirlineScheduleEntry
import datetime
from datetime import datetime,timedelta
import time
import airport
from airport.views import gettingairport
from django.views.generic import TemplateView,View,ListView, FormView
from airline.models import Rotations,BidPeriod
from user.models import Users
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
    elif len(objectsplit) == 2:  
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
    # now = '2018-11-01T05:10:29.398711Z'
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
        events = service.events().list(calendarId=calendarId, pageToken=page_token,timeMin=now,maxResults=10).execute()
        # for event in events['items']:
        #     print(event['summary'],event['start'])
        for event in events['items']:
            #getting all the rotation information and saving it in the 
            #rotation table for pay calculations
            rotation = Rotations()
            try:
                description = event['description']
            except KeyError:
                continue
            tripcreated = workingisotime(event['created'])
            summarysplit = event['summary'].split()
            
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
            else:
                rotation.userid = user_id
                rotation.rotationstart = tripstartzulu[0]
                rotation.rotationend = tripendzulu[0]
                rotation.rotationid = str(tripnum)
                rotation.googleimportdate = tripcreated[0]
                rotation.logbookimportdate = datetime.datetime.now()
                rotation.airline = airline
            # print(rotationsummary)
            
            for item in descriptionsplit:
                if item !='':
                    if item[0:3] == 'Rpt':
                        reporttimeraw = item[5:9]
                        reporttime = reporttimeraw[:2]+':'+reporttimeraw[2:]
                        reporttimeswitch = True
                        flightdate = (item[-5:])
                    if item[:3] =="DD ":
                        leg = item[3:]
                        legsplit = leg.split()
                        deadhead = True
                        fixingleg(tripyear,flightdate,reporttime,legsplit,tripnum,reporttimeswitch,deadhead,tripstartzulu[0])
                        reporttimeswitch = False
                    if item[:2] =="D " or item[:2] =="O ":
                        leg = item[2:]
                        legsplit = leg.split()
                        deadhead = True
                        fixingleg(tripyear,flightdate,reporttime,legsplit,tripnum,reporttimeswitch,deadhead,tripstartzulu[0])
                        reporttimeswitch = False

                    if item[:2] =="DL":
                        leg = item
                        legsplit = leg.split()
                        deadhead = False
                        fixingleg(tripyear,flightdate,reporttime,legsplit,tripnum,reporttimeswitch,deadhead,tripstartzulu[0])
                        reporttimeswitch = False
                    if 'TL' and 'BL' and 'CR' in item:
                        timesplit = item.split()
                        try:
                            if re.search('[0-9][0-9]:[0-9][0-9]',timesplit[0][:5]):
                                rotation.rotationpay = converttimetodecimal(timesplit[0][:5])
                        except IndexError:
                            rotation.rotationpay = 0
                        try:
                            if re.search('[0-9][0-9]:[0-9][0-9]',timesplit[1][:5]):
                                rotation.rotationblock = converttimetodecimal(timesplit[1][:5])
                        except IndexError:
                            rotation.rotationblock = 0
                        try:
                            if re.search('[0-9][0-9]:[0-9][0-9]',timesplit[2][:5]):
                                rotation.rotationcredit = converttimetodecimal(timesplit[2][:5])
                        except IndexError:
                            rotation.rotationcredit = 0
                    if item[:4] =="This":
                        eachword = item.split()
                        micrewexport = datetime.datetime.strptime(str(tripcreated[0].year)+'-'+eachword[4], '%Y-%d%b').date()
                        zulumicrew = converttoUTC(eachword[6],int(eachword[8][:3]))
                        combinedmicrew = addingtimeanddate(micrewexport,zulumicrew,int(eachword[8][:3]))
                        rotation.micrewexportdate = combinedmicrew
            if not Rotations.objects.filter(userid=user_id,rotationid=str(tripnum),rotationstart=tripstartzulu[0],rotationend=tripendzulu[0]).exists():
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
        flighttime.save()

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
        logbookdisplay = FlightTime.objects.all().filter(userid=getuserid(),scheduledflight=True,flightdate__gt=scheduledflightdatecutoff).order_by('flightdate','scheduleddeparttimelocal')
        return logbookdisplay

def showingrotationinfo():
    #used to start the rotation pay calculations. 
    months = BidPeriod.objects.filter()

class SimpleUpload(TemplateView):
    #used to upload pdf or csv files
    template_name = 'airline/upload.html'

    def post(self,form):
        nofile = "Test"
        userid=getuserid()
        perferences = Users.objects.get(user_id=userid)
        if 'myfile' not in self.request.FILES:
            nofile = "No File Selected"
            return render(self.request, 'airline/upload.html', {
            'nofile':nofile
        })
        myfile = self.request.FILES['myfile']
        filetype = myfile.name.split('.')
        count = 0
        if 'scheduled' in filetype[0] and filetype[1] =='csv':
            #adding scheduled flights to database. Should be a onetime use. 
            fs = FileSystemStorage('savedfiles')
            filename = fs.save(myfile.name, myfile)
            with open('./savedfiles/'+filename,'r') as read_file:
                logbook = csv.reader(read_file)
                zerohour = datetime.datetime.strptime('00:00:00', '%H:%M:%S').time()
                next(logbook)
                for item in logbook:
                    count += 1
                    if (count/50).is_integer():
                        print('still working',count)
                    deptimevalid = False
                    offtimevalid = False
                    ontimevalid = False
                    arrtimevalid = False
                    newtotal = False
                    #Getting the record from the database
                    if item[2] == '' or item[4] == '' or item[6] == '' or item[7] == '':
                        continue
                    try:
                        flight = FlightTime.objects.get(flightdate=item[2],departure=item[4],arrival=item[6],flightnum=item[7])
                    except (FlightTime.DoesNotExist, FlightTime.MultipleObjectsReturned) as error:
                        print(error)
                        with open('./savedfiles/dontexsist.csv','a') as outfile:
                            write = csv.writer(outfile)
                            write.writerow(item)

                    #getting flightdate and airport information
                    flightdate = flight.flightdate
                    unixdate = time.mktime(flightdate.timetuple())  
                    depairportinfo = gettingairportinfo(flight.departure,unixdate,flightdate)
                    arrairportinfo = gettingairportinfo(flight.arrival,unixdate,flightdate)

                    #Filling the Off and On times and calculating flight time
                    if flight.offtime == zerohour and item[9] != '':
                        flight.offtime = item[9]
                        offtimevalid = True

                    if flight.ontime == zerohour and item[10] != '':
                        flight.ontime = item[10]
                        ontimevalid = True

                    if flight.flighttime == 0 and flight.offtime != '' and flight.ontime != '':
                        flight.flighttime = calculatetimes(str(flight.offtime)[:5],str(flight.ontime)[:5],perferences.decimalplaces,perferences.decimal)
                    elif item[52] != '':
                        flight.flighttime = item[52]

                    # adding the scheduled departure times and arrival times from the CSV file
                    if not item[47] == '':
                        flight.scheduleddeparttime = item[47]
                    if not item[48] == '':
                        flight.scheduledarrivaltime = item[48]

                    #calculating scheduled block
                    if item[49] != '':
                        flight.scheduledblock = item[49]
                    elif item[49] == '' and flight.scheduleddeparttime != None and flight.scheduledarrivaltime != None:
                        flight.scheduledblock = calculatetimes(flight.scheduleddeparttime,flight.scheduledarrivaltime,perferences.decimalplaces,perferences.decimal)

                    # Calculating minutes under
                    if flight.total != None and flight.scheduledblock != None:
                        if Decimal(flight.total) < Decimal(flight.scheduledblock):
                            flight.minutesunder = Decimal(flight.scheduledblock)-Decimal(flight.total)
                    elif item[62] != '':
                        flight.minutesunder = item[62]

                    flight.rotationid = item[50]

                    if flight.deptime != None and item[56] == '':
                        flight.deptimelocal = converttolocal(str(flight.deptime)[:5],depairportinfo[0]['gmt_offset_single'])
                    elif not item[56] == '':
                        flight.deptimelocal = item[56]

                    if flight.offtime != None and item[57] == '':
                        flight.offtimelocal = converttolocal(str(flight.offtime)[:5],depairportinfo[0]['gmt_offset_single'])
                    elif not item[57] == '':
                        flight.offtimelocal = item[57]

                    if flight.ontime != None and item[58] == '':
                        flight.ontimelocal=converttolocal(str(flight.ontime)[:5],arrairportinfo[0]['gmt_offset_single'])
                    elif not item[58] =='':
                        flight.ontimelocal = item[58] 

                    if flight.arrtime != None and item[59] == '':
                        flight.arrtimelocal=converttolocal(str(flight.arrtime)[:5],arrairportinfo[0]['gmt_offset_single'])
                    elif not item[59] =='':
                        flight.arrtimelocal = item[59] 

                    if not item[60] =='':
                        flight.reporttime = item[60]
                        flight.reporttimelocal = item[61]

                    flight.flightupdated = datetime.datetime.now()

                    if flight.deptime != None and flight.arrtime != None:
                        flight.scheduledflight = False
                    elif item[68] != '':
                        flight.scheduledflight = item[68]

                    if not item[69] == '':
                        flight.deadheadflight = item[69]

                    if not item[70] =='':
                        flight.startdate = item[70]

                    flight.departuregate = item[71]
                    flight.arrivalgate = item[72]
                    flight.flightpath = item[73]
                    if not item[74] == '':
                        flight.airspeed = item[74]
                    if not item[75] == '':
                        flight.filedalt = item[75]

                    flight.save()
            nofile='Scheduled information saved to the database'
        if filetype[1] =='csv' and not 'scheduled' in filetype[0]:
            #takes the output file and saves it to the database. Will recalulate anything that is blank but can be calculated based on OOOI times other wise it will just post whatever it has. 
            fs = FileSystemStorage('savedfiles')
            filename = fs.save(myfile.name, myfile)
            with open('./savedfiles/'+filename,'r') as read_file:
                logbook = csv.reader(read_file)
                next(logbook)
                for item in logbook:
                    deptimevalid = False
                    offtimevalid = False
                    ontimevalid = False
                    arrtimevalid = False
                    newtotal = False
                    flight=FlightTime()
                    if len(item) < 75:
                        continue
                    # flight.id =item[0]
                    flight.userid = userid
                    if not item[2] == '':
                        flight.flightdate =item[2]
                        flightdate = datetime.datetime.strptime(item[2],'%Y-%m-%d')
                        unixdate = time.mktime(flightdate.timetuple())  
                    aircraft_type = NewPlaneMaster.objects.get(nnumber=item[3])
                    flight.aircraftId = aircraft_type
                    if not item[4] == '':
                        flight.departure = item[4]
                        depairportinfo = gettingairportinfo(item[4],unixdate,flightdate)
                    flight.route = item[5]
                    if not item[6] == '':
                        flight.arrival = item[6]
                        arrairportinfo = gettingairportinfo(item[6],unixdate,flightdate)
                    
                    flight.flightnum = item[7]
                    if not item[8] == '':
                        flight.deptime  = item[8]
                        if item[8] != '00:00:00':
                            deptime = item[8]
                            deptimevalid = True
                    if not item[9] == '':
                        flight.offtime = item[9]
                        if item[9] != '00:00:00':
                            offtime = item[9]
                            offtimevalid = True
                    if not item[10] == '':
                        flight.ontime = item[10]
                        if item[10] != '00:00:00':
                            ontime = item[10]
                            ontimevalid = True
                    if not item[11] == '':    
                        flight.arrtime = item[11]
                        if item[11] != '00:00:00':
                            arrtime = item[11]
                            arrtimevalid = True
                    if deptimevalid and arrtimevalid and item[26] == '':
                        flight.total = calculatetimes(deptime,arrtime,perferences.decimalplaces,perferences.decimal)
                        newtotal = True
                    elif item[26] != '':
                        flight.total = item[26]
                    if offtimevalid and ontimevalid and item[52] == '':
                        flight.flighttime = calculatetimes(offtime,ontime,perferences.decimalplaces,perferences.decimal)
                    elif item[52] != '':
                        flight.flighttime = item[52]
                    
                    if perferences.cx and item[4] != '' and item[6] !='' and item[53] == '':
                        distance = (great_circle((depairportinfo[0]['airport']['lat'],depairportinfo[0]['airport']['long']),(arrairportinfo[0]['airport']['lat'],arrairportinfo[0]['airport']['long'])).nm)

                        flight.distance = distance
                        if distance > 50 and item[24] == '':
                            flight.crosscountry = flight.total
                    elif item[53] != '':
                        flight.distance = item[53]
                    
                    if item[24] != '':
                            flight.crosscountry = item[24]
                    

                    if not item[12] == '':
                        flight.landings = item[12]
                    else:
                        flight.landings = 0
                    if not item[13] == '':
                        flight.imc = item[13]
                    if not item[14] == '':
                        flight.hood = item[14]
                    if not item[15] == '':
                        flight.iap = item[15]
                    flight.typeofapproach = item[16]
                    flight.descriptionofapproach = item[17]
                    if not item[18] == '':
                        flight.holdnumber = item[18]
                    if not item[19] == '':
                        flight.holdboolean = item[19]
                    if newtotal and perferences.pic and item[20] == '':
                        flight.pic = flight.total
                    elif item[20] != '':
                        flight.pic = item[20]
                    
                    if newtotal and perferences.sic and item[21] == '':
                        flight.sic = flight.total
                    elif item[21] != '':
                        flight.sic = item[21]
                    
                    if newtotal and perferences.cfi and item[22] == '':
                        flight.cfi = flight.total
                    elif item[22] != '':
                        flight.cfi = item[22]

                    if newtotal and perferences.dual and item[23] == '':
                        flight.dual = flight.total
                    elif item[23] != '':
                        flight.dual = item[23]

                    if newtotal and perferences.solo and item[25] == '':
                        flight.solo = flight.total
                    elif item[25] != '':
                        flight.solo = item[25]
                    
                    if item[27] == '' and item[29] == '' and deptimevalid and arrtimevalid and item[4] != '' and item[6] != '':
                        #getting the times all set correctly to work on the night time calculations
                        departuretime = addingtimeanddate(flightdate,deptime,depairportinfo[0]['gmt_offset_single'])
                
                        #if departure date gets one added to it then automatically add it to the arrival date, else run the formula on arrival date separately
                        
                        if departuretime>(flightdate+timedelta(days=1)) :
                            arrivaltime = datetime.datetime.combine((flightdate + timedelta(days=1)),datetime.datetime.strptime(arrtime,'%H:%M').time())
                        else:
                            arrivaltime = addingtimeanddate(flightdate,arrtime,arrairportinfo[0]['gmt_offset_single'])
                        
                        #getting the previous sunset and the nextday sunrise, so I will know the times for both nights
                        extrasuntimesdep = getextrasuntimes(item[4],flightdate)
                        extrasuntimesarr = getextrasuntimes(item[6],flightdate)
                        
                        nightcalc = nighttime(flight.total,departuretime,arrivaltime,extrasuntimesdep[0],depairportinfo[1]['sunriseUTC'],depairportinfo[1]['sunsetUTC'],extrasuntimesdep[1],extrasuntimesarr[0],arrairportinfo[1]['sunriseUTC'],arrairportinfo[1]['sunsetUTC'],extrasuntimesarr[1],int(flight.landings))
                
                        flight.night = nightcalc[0]
                        flight.day = nightcalc[1]
                        if int(flight.landings) > 0:
                            flight.nightlandings = nightcalc[2]
                            flight.daylandings = nightcalc[3]
                    else:
                        if not item[27] == '':
                            flight.day = item[27]
                        if not item[28] == '':
                            flight.daylandings = item[28]
                        if not item[29] == '':
                            flight.night = item[29]
                        if not item[30] == '':
                            flight.nightlandings = item[30]
                    flight.printcomments = item[31]
                    flight.personalcomments = item[32]
                    if not item[33] == '':
                        flight.ftd = item[33]
                    if not item[34] == '':    
                        flight.ftdimc = item[34]
                    if not item[35] == '':
                        flight.sim = item[35]
                    if not item[36] == '':
                        flight.simimc = item[36]
                    if not item[37] == '':
                        flight.pcatd = item[37]
                    if not item[38] == '':
                        flight.pcimc = item[38]
                    flight.instructor = item[39]
                    if item[40] != '':
                        flight.instructorid = item[40]
                    flight.student = item[41]
                    if item[42] !='':
                        flight.studentid = item[42]
                    flight.captain = item[43]
                    flight.firstofficer = item[44]
                    flight.flightattendants = item[45]
                    if not item[46] == '':
                        flight.passengercount = item[46]
                    if not item[47] == '':
                        flight.scheduleddeparttime = item[47]
                    if not item[48] == '':
                        flight.scheduledarrivaltime = item[48]
                    if not item[49] == '':
                        flight.scheduledblock = item[49]
                    flight.rotationid = item[50]
                    flight.aircrafttype = aircraft_type.aircraftmodel
                    if item[47] != '' and item[54] == '':
                        flight.scheduleddeparttimelocal = converttolocal(item[47][:5],depairportinfo[0]['gmt_offset_single'])
                    elif item[54] != '':
                        flight.scheduleddeparttimelocal = item[54]
                    if item[48] != '' and item[55] == '':
                        flight.scheduledarrivaltimelocal = converttolocal(item[48][:5],depairportinfo[0]['gmt_offset_single'])
                    elif item[55] != '':
                        flight.scheduledarrivaltimelocal = item[55]
                    if not item[4] == '' and deptimevalid:
                        flight.deptimelocal = converttolocal(deptime[:5],depairportinfo[0]['gmt_offset_single'])
                    elif not item[56] == '':
                        flight.deptimelocal = item[56]
                    if not item[4] == '' and offtimevalid:
                        flight.offtimelocal = converttolocal(offtime[:5],depairportinfo[0]['gmt_offset_single'])
                    elif not item[57] == '':
                        flight.offtimelocal = item[57]
                    if not item[6] == '' and ontimevalid:
                        flight.ontimelocal=converttolocal(ontime[:5],arrairportinfo[0]['gmt_offset_single'])
                    elif not item[58] =='':
                        flight.ontimelocal = item[58] 
                    if not item[6] == '' and arrtimevalid:
                        flight.arrtimelocal=converttolocal(arrtime[:5],arrairportinfo[0]['gmt_offset_single'])
                    elif not item[59] =='':
                        flight.arrtimelocal = item[59] 
                    if not item[60] =='':
                        flight.reporttime = item[60]
                        flight.reporttimelocal = item[61]
                    if flight.total != None and flight.scheduledblock != None:
                        if Decimal(flight.total) < Decimal(flight.scheduledblock):
                            flight.minutesunder = Decimal(flight.scheduledblock)-Decimal(flight.total)
                    elif item[62] != '':
                        flight.minutesunder = item[62]
                    flight.flightupdated = datetime.datetime.now()
                    if item[64] != '':
                        flight.flightcreated = item[64]
                    if not item[4] == '' and not item[6] =='':
                        if depairportinfo[0]['airport']['country'] != 'US' or arrairportinfo[0]['airport']['country'] != 'US': 
                            flight.international = True
                            flight.domestic = False
                        else: 
                            flight.international = False
                            flight.domestic = True
                    elif not item[65] == '' and item[66] != '':
                        flight.domestic = item[65]
                        flight.international = item[66]
                    flight.paycode = item[67]
                    if deptimevalid and arrtimevalid:
                        flight.scheduledflight = False
                    elif item[68] != '':
                        flight.scheduledflight = item[68]
                    if not item[69] == '':
                        flight.deadheadflight = item[69]
                    if not item[70] =='':
                        flight.startdate = item[70]
                    flight.departuregate = item[71]
                    flight.arrivalgate = item[72]
                    flight.flightpath = item[73]
                    if not item[74] == '':
                        flight.airspeed = item[74]
                    if not item[75] == '':
                        flight.filedalt = item[75]
                    flight.save()
            nofile='Logbook information saved to the database'
            
        if filetype[1] =='pdf' and 'delta' in filetype[0]:
            airline = perferences.airline
            fs = FileSystemStorage('savedfiles')
            fs.save(myfile.name, myfile)
            reader = PdfReader(myfile)
            numpages = reader.numPages
            broken = False
            for i in range(0,numpages):
                page = reader.pages[i]
                text = page.extract_text()
                textsplit = text.split('\n')
                for item in textsplit:
                    itemsplit = item.split(' ')
                    if broken == True:
                        break
                        
                    if len(itemsplit) > 7:
                        aircraft = NewPlaneMaster()
                        if itemsplit[0].isnumeric():
                            try:
                                NewPlaneMaster.objects.get(nnumber=itemsplit[2])
                                print(itemsplit[0],itemsplit[1],itemsplit[2],itemsplit[3],itemsplit[4])
                                continue
                            except:
                                aircraft.shipnumber = itemsplit[0]
                                aircraft.configuration = itemsplit[1]
                                aircraft.nnumber = itemsplit[2]
                                aircraft.serialnumber = itemsplit[3]
                                aircraft.manufacturedate = itemsplit[4]
                                if itemsplit[1][0] == '7':
                                    try:
                                        modifiedsplit = itemsplit[0],itemsplit[1],itemsplit[2],itemsplit[3],itemsplit[4],itemsplit[6],itemsplit[7],itemsplit[8]
                                        
                                    except:
                                        print(itemsplit)
                                elif itemsplit[5] == "TRENT":
                                    modifiedsplit = itemsplit[0],itemsplit[1],itemsplit[2],itemsplit[3],itemsplit[4],itemsplit[5]+'-'+itemsplit[6],itemsplit[7],itemsplit[8]
                                else:
                                    modifiedsplit = itemsplit[0],itemsplit[1],itemsplit[2],itemsplit[3],itemsplit[4],itemsplit[5],itemsplit[6],itemsplit[7]
                                with open('./savedfiles/fleet.csv','a') as outfile:
                                    write = csv.writer(outfile)
                                    write.writerow(modifiedsplit)

                    if itemsplit[0] == 'THESE':
                        broken = True
                        break
                        
                            
            nofile='Aircraft File Successfully Processed'
        if filetype[1] =='pdf' and not 'delta' in filetype[0]:
            
            airline = perferences.airline
            reader = PdfReader(myfile)
            title = ((reader.pages[0]).extract_text()).split()
            bidstart = datetime.datetime.strptime(title[8]+title[9]+title[10],'%B%d,%Y').date()
            bidend = datetime.datetime.strptime(title[12]+title[13]+title[14],'%B%d,%Y').date()
            bidperioddays = ((bidend-bidstart).days)+1
            fs = FileSystemStorage('savedfiles')
            fs.save(myfile.name, myfile)
            for i in range(3,6):
                page = reader.pages[i]
                text = page.extract_text()
                textsplit = text.split(' ')
                line = []
                wholelist = []
                for item in textsplit:
                    if '\n' in item:
                        line = []
                        base=item[-3:]
                        line.append(base)
                    elif item != '':
                        line.append(item)
                    
                    if len(line) == 9:
                        wholelist.append(line)
                
                for cat in wholelist:
                    bidperiod = BidPeriod()
                    if len(cat[0]+cat[1]+cat[2]) == 7:
                        category = (cat[0]+cat[1]+cat[2])
                        alvstart = cat[3].split(':')
                        alv = int(alvstart[0])+round(int(alvstart[1])/60,2)
                        alvrange = cat[4]
                        reserve = cat[5]
                        pattern = cat[6]
                        if cat[7] == 'Yes':
                            extraday = True
                        if cat[7] == 'No':
                            extraday = False
                        rll = int(cat[8])
                        
                        if not BidPeriod.objects.filter(airline=airline,bidperiodstart=bidstart,bidperiodend=bidend,category=category).exists():
                            bidperiod.calendarmonth = bidstart.month
                            bidperiod.bidperiodstart = bidstart
                            bidperiod.bidperiodend = bidend
                            bidperiod.alv = alv
                            bidperiod.alvrange = alvrange
                            bidperiod.resguarentee = reserve
                            bidperiod.reserverules = pattern
                            bidperiod.extraday = extraday
                            bidperiod.rll = rll
                            bidperiod.airline = airline
                            bidperiod.category = category
                            bidperiod.bidperioddays = bidperioddays
                            bidperiod.save()
                nofile='File Successfully Uploaded'
        return render(self.request, 'airline/upload.html', {
            'nofile':nofile
        })


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
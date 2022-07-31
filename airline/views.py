
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import AirlineScheduleEntry
import datetime
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
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

@login_required(login_url='/')
def airlinehome(request):
    return render(request, 'airline/schedule.html', {})


        

class DeltaScheduleEntry(FormView):
    
    template_name = 'airline/schedule.html'
    form_class = AirlineScheduleEntry
    success_url = '/airline'

    
    def form_valid(self,form):
        print(form)
        form.save()
        return super().form_valid(form)


# def workdeltschedule(request):
#     if request.method =='POST':
#         schedule = request.POST.get('schedule')
#         trip = []
#         count = 0
#         base = preferences()
#         schedulesp = schedule.splitlines()
#         # year = schedulesp[1]
#         add = 'yes'
#         for count,line in enumerate(schedulesp):
#             print(line)
#             # #Get Rotation Number
#             # if line == 'OPER':
#             #     rotation = schedulesp[count+1]
#             #     trip.append(rotation)
            
#             # #gettting starting date
#             # if line == 'EFFECTIVE':
#             #     startdate = schedulesp[count+1]
#             #     trip.append(startdate)
            
#             # #gettting first day of trip
#             # if line == 'EQP':
#             #     firstleg = schedulesp[count+1],schedulesp[count+2],schedulesp[count+3],schedulesp[count+4]
#             #     trip.append(firstleg)

#             # if line == 'ACTUAL':
#             #     if schedulesp[count + 1] == 'REPORT':
#             #         if schedulesp[count + 2] == 'TIME':
#             #             print(schedulesp[count + 3])
#             # if len(line) < 10:
#             #     print(line[:5])
#             # if re.match("[0-9][0-9]",line[:1]):
#             #     print(line)
#             #     trip.append
    
#         return render(request, 'airline/schedule.html', {'schedule':schedulesp})
#     else:
#         return render(request, 'airline/schedule.html', {})



# # def oldworkingsechedule():
            
# #             if line == base:
# #                 month.append(trip)
# #                 trip = []
# #             if line == 'Layover':
# #                 add = 'no'
# #             if re.match("[0-9][0-9][A-Z][a-z][a-z]",line):
# #                 add = 'yes'
# #                 currentdate = datetime.datetime.strptime(line[0:2]+' '+line[2:6]+' '+ year,"%d %b %Y")
              
# #             if add == 'yes' and line != base and line != 'to':
# #                 if '-' in line:
# #                     dept = line.split('-')
# #                     trip.append(dept[0])
# #                     trip.append(dept[1])
# #                 elif '#' in line: 
# #                     trip.append(currentdate)
# #                     trip.append(line[1:])
# #                 else:
# #                     trip.append(line)
# #         month.append(trip)  
# #         monthfinal = []
# #         for trip in month:
# #             for count,leg in enumerate(trip):
# #                 tripnumber = trip[0]
                
# #                 if type(leg) == datetime.datetime:
# #                     unixtime = time.mktime(leg.timetuple())
# #                     flightnum = trip[count + 1]
                    
# #                     departairportinfo = gettingairport(trip[count + 2],unixtime)

# #                     departairport = departairportinfo['airport']['icao']

# #                     departuretime = time.mktime(
# #                         datetime.datetime.combine(leg,datetime.datetime.strptime(trip[count+4],"%H%M").time())
# #                         .timetuple())-departairportinfo['timezoneinfo']['gmt_offset']
                    
# #                     arrivalairportinfo = gettingairport(trip[count + 3],unixtime)
# #                     arrivalairport = arrivalairportinfo['airport']['icao']
# #                     arrivaltime = time.mktime(
# #                         datetime.datetime.combine(leg,datetime.datetime.strptime(trip[count+5],"%H%M").time())
# #                         .timetuple())-arrivalairportinfo['timezoneinfo']['gmt_offset']
# #                     legtotal = [leg,flightnum,departairport,arrivalairport,departuretime,arrivaltime,round(((arrivaltime-departuretime)/60/60),2),trip[count+6],tripnumber]
                    
# #                     monthfinal.append(legtotal)
                    
# #         for leg in monthfinal:
# #             print(leg)
        

# def preferences():
      
#             # if line == 'Names':
#             #     add = 'no'
#             # if line == 'A':
#             #     captain = 'add'
#             # if add == 'no' and captain == 'add':
#             #     captainname.append(line)
#             # if line == 'REG' and fo == '':
#             #     captain = ''
#             #     trip.append(captainname)
#             #     captainname = []
#             #     fo = 'add'
#             # if add == 'no' and fo == 'add':
#             #     foname.append(line)
#             # if line == 'REG' and captain == '':
#             #     trip.append(foname)
#             #     fo = ''
#             #     foname = []
#             #     add = 'yes'
#     base = 'MSP'
#     return base
# # def returndate(currentyear,currentdate):
# def workdeltschedulegoogle(request):
    

#     # If modifying these scopes, delete the file token.json.
#     SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    
#     creds = None
#     # The file token.json stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())

#     try:
#         service = build('calendar', 'v3', credentials=creds)

#         # Call the Calendar API
#         now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
#         calendarId='jb360v1bcsqt0m7cf7sja0i06g@group.calendar.google.com'
#         page_token = None
#         schedule = []
#         trip = []
#         monthsum = []
#         while True:
#             events = service.events().list(calendarId='jb360v1bcsqt0m7cf7sja0i06g@group.calendar.google.com', pageToken=page_token,timeMin=now).execute()
#             for event in events['items']:
#                 summary = re.sub(r'\n','',event['summary'])
#                 tripnum = summary[0:4]
#                 triptimes = summary[-11:]
                
#                 # schedule.append(summary)
#                 # description = re.sub(r'\n','',event['description'])
#                 description = event['description']
                
#                 descriptionsplit = description.split()
#                 # print(descriptionsplit)

#                 for count,item in enumerate(descriptionsplit):
                    
#                     match = re.search("[0-3][0-9][A-Z][A-Z][A-Z]",item)
#                     if match:
#                             flightdate = item
#                     if item[0:2] =="DL":
#                         flightnum = item[2:7]
#                         depart = descriptionsplit[count+1][:3]
#                         arr = descriptionsplit[count+1][-3:]
#                         deptime = descriptionsplit[count+2][:5]
#                         arrtime = descriptionsplit[count+2][-5:]
#                         leg = [flightdate,flightnum,depart,arr,deptime,arrtime,tripnum]
#                         trip.append(leg)
#                         leg=[]
#                 monthsum.append(trip)  
#                 trip=[]      
            
#                 # schedule.append(description)
                
#             page_token = events.get('nextPageToken')
#             if not page_token:
#                 break
        

#     except HttpError as error:
#         print('An error occurred: %s' % error)

#     for item in (monthsum):
        
#         print(item)

#     return render(request, 'airline/masterschedule.html', {'schedule': monthsum})
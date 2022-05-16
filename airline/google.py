from __future__ import print_function

import datetime
import os.path
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
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
                'credentials.json', SCOPES)
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
        schedule = []
        trip = []
        monthsum = []
        while True:
            events = service.events().list(calendarId='jb360v1bcsqt0m7cf7sja0i06g@group.calendar.google.com', pageToken=page_token,timeMin=now).execute()
            for event in events['items']:
                summary = re.sub(r'\n','',event['summary'])
                tripnum = summary[0:4]
                triptimes = summary[-11:]
                
                # schedule.append(summary)
                # description = re.sub(r'\n','',event['description'])
                description = event['description']
                
                descriptionsplit = description.split()
                # print(descriptionsplit)

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

    for item in (monthsum):
        
        print(item)
        
if __name__ == '__main__':
    main()
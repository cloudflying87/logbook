from cmath import log
import os
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from user.views import getuserid
from django.views.generic.base import TemplateView
from django.views.generic import FormView, DetailView
from django.views.generic.list import ListView
from aircraft.models import AircraftModel, Manufacture, NewPlaneMaster
from airport.views import airporthome
from logbook.models import FlightTime
from django.db.models.functions import ExtractYear
from reports.forms import DateSelector
from user.models import Users
from django.contrib.auth.models import User
from django_currentuser.middleware import (
    get_current_user)

from airline.views import flightaware
from django.core.paginator import Paginator
from django.db.models import Count,Sum,Avg
from django.db.models.functions import Round
from django.db.models import Q
import datetime
import requests
import csv
from django.http import HttpResponse, FileResponse
import io
from reportlab.pdfgen import canvas

@login_required(login_url='/')
def reporthome(request):
    print('hello')


def callingdatabasedates(startdate,enddate,userid):
    if type(startdate) == str and type(enddate) == str:
        flights = FlightTime.objects.filter(userid=userid,flightdate__gt=startdate,flightdate__lt=enddate).exclude(scheduledflight=True,deadheadflight=True)
    if type(startdate) == bool and type(enddate) == bool:
            flights = FlightTime.objects.filter(userid=userid).exclude(scheduledflight=True,deadheadflight=True)
    if type(startdate) == str and type(enddate) == bool:
        flights = FlightTime.objects.filter(userid=userid,flightdate__gt=startdate).exclude(scheduledflight=True,deadheadflight=True)
    if type(startdate) == bool and type(enddate) == str:
        flights = FlightTime.objects.filter(userid=userid,flightdate__lt=enddate).exclude(scheduledflight=True,deadheadflight=True)

    return flights
class ReportBase(TemplateView):
    model = FlightTime
    context_object_name = "flight"
    template_name = 'reports/basereport.html'
class TotalsOnly(TemplateView):
    template_name = 'reports/totaldisplay.html'
    def get(self, *args, **kwargs):
        pagetitle = "Totals Report"
        userid = getuserid()
        qs = {
            'total' : FlightTime.objects.all().filter(userid=userid).     aggregate(
                total = Sum('total'),
                day = Sum('day'),
                daylandings = Sum('daylandings'),
                night = Sum('night'),
                nightlandings = Sum('nightlandings'),
                solo = Sum('solo'),
                pic = Sum('pic'),
                sic=Sum('sic'),
                dual = Sum('dual'),
                cfi = Sum('cfi'),
                imc= Sum('imc'),
                hood= Sum('hood'),
                iap= Sum('iap'),
                holdnumber= Sum('holdnumber'),
                crosscountry= Sum('crosscountry'),
                pax = Sum('passengercount'),
                miles = Sum('distance')
            ),

            'totalflights': FlightTime.objects.all().filter(userid=userid).exclude(Q(scheduledflight=1) | Q(total=0)).aggregate(
            tflight = Count('flightdate'))}
        return self.render_to_response({"qs":qs, "title":pagetitle})

class Lookup(TemplateView):
    template_name = 'reports/lookup.html'
    def get(self, request, *args, **kwargs):
        pagetitle = "Look-Up"
        return self.render_to_response({"title":pagetitle})

class TopAirports(TemplateView):
    template_name = 'reports/topairports.html'
    
    def get(self, request, *args, **kwargs):
        airportcount = []
        makedict = []
        pagetitle = "Airports"
        userid = getuserid()
        topfive =  FlightTime.objects.filter(userid=userid).values('departure').distinct()
        
        for airport in topfive:
            
            info = FlightTime.objects.filter(Q(departure=airport['departure']) | Q(arrival=airport['departure']),userid=userid).exclude(Q(scheduledflight=1) | Q(total=0)).aggregate(
                operations = Count('flightdate'),
                landings = Sum('landings'))
            
            if airport['departure'] != None:
                airportdata = (info['operations'],airport['departure'],info['landings'])
                airportcount.append(airportdata)
        airportcount.sort(reverse=True)
        topten = airportcount[:10]

        for airport in topten:
            dictitem= {'airport':airport[1],'times':airport[0],'landings':airport[2]}
            makedict.append(dictitem)
        
        return self.render_to_response({'depart':makedict,"title":pagetitle,'unique':len(topfive)})
class TotalsDisplay(TemplateView):
    template_name = 'reports/datebase.html'

class TotalsByDate(TemplateView):
    template_name = 'reports/totalsbydate.html'
    
    def get(self, request, *args, **kwargs):
        yeartotals = []
        years = []
        labels =[]
        pax = []
        miles = []
        pagetitle = "Totals By Date"
        userid = getuserid()
        logbookyears = FlightTime.objects.filter(userid=userid).annotate(year=ExtractYear('flightdate')).values('year').distinct()

        for logyear in logbookyears:
            info = FlightTime.objects.filter(userid=userid,flightdate__year=logyear['year']).aggregate(
                    airtotal = Sum('total'),
                    miletotal = Sum('distance'),
                    paxtotal = Sum('passengercount'),
                    flighttotal = Count('total'),
                    avgflight = Avg('total'),
                    avgdistance = Avg('distance'),
                    avgpax = Avg('passengercount')
            )
            label = logyear['year']
            data = float(info['airtotal'])
            paxtotal = int(info['paxtotal'])
            milestotal = int(info['miletotal'])
            totalyear = {'year':logyear['year'],'airtotal':info['airtotal'],'pax':info['paxtotal'],'miles':info['miletotal'],'flighttotal':info['flighttotal'],'avgflight':round(info['avgflight'],2),'avgdistance':int(info['avgdistance']),'avgpax':int(info['avgpax'])}
            yeartotals.append(data)
            labels.append(label)
            pax.append(paxtotal)
            miles.append(milestotal)
            years.append(totalyear)
        
        return self.render_to_response({"yeartotals":yeartotals,'labels':labels,'years':years,'pax':pax,'miles':miles,"title":pagetitle})

class PilotSearch(TemplateView):
    template_name = 'reports/pilotsearch.html'

    def post(self, request, *args, **kwargs):
        userid=getuserid()
        pagetitle = "Pilot Lookup"
        pilotlookup = request.POST['PilotSearch']

        info = FlightTime.objects.filter(Q(captain__icontains=pilotlookup)|Q(firstofficer__icontains=pilotlookup),userid=userid).aggregate(
                    airtotal = Sum('total'),
                    miletotal = Sum('distance'),
                    paxtotal = Sum('passengercount'),
                    flighttotal = Count('total'),
                    avgflight = Avg('total'),
                    avgdistance = Avg('distance'),
                    avgpax = Avg('passengercount')
            )
        
        flights = FlightTime.objects.filter(Q(captain__icontains=pilotlookup)|Q(firstofficer__icontains=pilotlookup),userid=userid).exclude(scheduledflight=True).order_by('-flightdate')
        print(info,flights)
        return self.render_to_response({"title":pagetitle,'info':info,'flights':flights})
class FlightAware(TemplateView):
    template_name = 'reports/flightaware.html'

    def get(self, request, *args, **kwargs):
        
        pagetitle = "Flightaware API"
        
        ident = 'SKW5244'
        startdate = '2015-12-23T00:00Z'
        enddate = '2015-12-23T23:25Z'
        params = {"start":startdate,"end":enddate}
        endpoint = "https://aeroapi.flightaware.com/aeroapi/history/flights/{fident}"
        url = endpoint.format(fident=ident)
        
        headers = {'x-apikey': os.getenv('flightawareapi')}
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:  # SUCCESS
            result = response.json()
            print(result['flights'])
            departairport = result['flights'][0]['origin']['code_icao']
            arrivalairport = result['flights'][0]['destination']['code_icao']
            tailnumber = result['flights'][0]['registration']
            scheduledout = result['flights'][0]['scheduled_out']
            actualout = result['flights'][0]['actual_out']
            scheduledoff = result['flights'][0]['scheduled_off']
            actualoff = result['flights'][0]['actual_off']
            scheduledon = result['flights'][0]['scheduled_on']
            actualon = result['flights'][0]['actual_on']
            scheduledin = result['flights'][0]['scheduled_in']
            actualin = result['flights'][0]['actual_in']
            departgate = result['flights'][0]['gate_origin']
            arrivalgate = result['flights'][0]['gate_destination']
            airspeed = result['flights'][0]['filed_airspeed']
            filedalt = result['flights'][0]['filed_altitude']
            route = result['flights'][0]['route']

            flight = {'departairport':departairport, 'arrivalairport':arrivalairport, 'tailnumber':tailnumber,'scheduleddeparttime': scheduledout, 'actualout': actualout,'scheduledoff':scheduledoff,'actualoff':actualoff,'scheduledon':scheduledon,'actualon':actualon,'scheduledin':scheduledin,'actualin':actualin, 'departgate':departgate,'arrivalgate':arrivalgate,'airspeed':airspeed,'filedalt':filedalt,'route':route}
        else:
            flight = 'Missing'
        
        return self.render_to_response({"title":pagetitle,"info":flight})

class FlightawareRequest(FormView):
    template_name = 'reports/importpastflighttimes.html'
    form_class = DateSelector
    success_url = '/reports/dates'

    def form_valid(self,form):
        userid=getuserid()
        if form['frombeginning'].value():
            startdate = True
        else:
            startdate = form['startdate'].value()

        if form['toend'].value():
            enddate = True
        else:
            enddate = form['enddate'].value()

        flights = callingdatabasedates(startdate,enddate,userid)
        count = 0
        print(len(flights))
        historylist = []
        for flight in flights:
            count = count + 1
            if (count/25).is_integer():
                print('still working',count)
            flightdate = datetime.datetime.strftime(flight.flightdate, '%Y-%m-%d')
            starttime = flightdate + 'T' + datetime.time.strftime(flight.deptime,'%H:%M') +'Z'
            endtime = flightdate + 'T' + datetime.time.strftime(flight.arrtime,'%H:%M') +'Z'
            if flight.flightdate < datetime.datetime.strptime('2018-02-20','%Y-%m-%d').date():
                flightnum = 'SKW'+ str(flight.flightnum)
            else:
                flightnum = 'DAL'+ str(flight.flightnum)
            
            

            history = flightaware(flightnum,starttime,endtime)
            if history != 'missing':
                flightlist = flight.flightdate,flight.aircraftId,history['tailnumber'],flight.departure,history['departairport'],flight.arrival,history['arrivalairport'],flight.flightnum,history['flightnum'],flight.deptime,history['actualout'],flight.offtime,history['actualoff'],flight.ontime,history['actualon'],flight.arrtime,history['actualin'],flight.landings,flight.imc,flight.total,flight.day,flight.daylandings,flight.night,flight.nightlandings,flight.printcomments,flight.personalcomments,flight.captain,flight.firstofficer,flight.flightattendants,flight.passengercount,flight.scheduleddeparttime,history['scheduledout'],history['scheduledoff'],history['scheduledon'],flight.scheduledarrivaltime,history['scheduledin'],flight.scheduledblock,flight.rotationid,flight.aircrafttype,flight.flighttime,flight.distance,history['departgate'],history['arrivalgate'],history['airspeed'],history['filedalt'],history['route']
            else:
                flightlist = flight.flightdate,flight.aircraftId,'',flight.departure,'',flight.arrival,'',flight.flightnum,'',flight.deptime,'',flight.offtime,'',flight.ontime,'',flight.arrtime,'',flight.landings,flight.imc,flight.total,flight.day,flight.daylandings,flight.night,flight.nightlandings,flight.printcomments,flight.personalcomments,flight.captain,flight.firstofficer,flight.flightattendants,flight.passengercount,flight.scheduleddeparttime,'','','',flight.scheduledarrivaltime,'',flight.scheduledblock,flight.rotationid,flight.aircrafttype,flight.flighttime,flight.distance,'','','','',''
            historylist.append(flightlist)

        
        response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment;' f'filename="flighttime{startdate}-{enddate}.csv'},
        )

        writer = csv.writer(response)

        writer.writerow(['flightdate','aircraftId','aircraftFA','departure','departureFA','arrival','arrivalFA','flightnum','flightnumFA','deptime', 'deptimeFA', 'offtime','offtimeFA','ontime','ontimeFA','arrtime','arrtimeFA','landings','imc','total','day','daylandings','night','nightlandings','printcomments','personalcomments','captain', 'firstofficer','flightattendants','passengercount','scheduleddeparttime','scheduleddeparttimeFA','scheduledoffFA','scheduledonFA','scheduledarrivaltime','scheduledarrivaltimeFA','scheduledblock','rotationid','aircrafttype','flighttime','distance','departgate','arrivalgate','airspeed','filedalt','route'])
        for leg in historylist:
            writer.writerow([leg[0],leg[1],leg[2],leg[3],leg[4],leg[5],leg[6],leg[7],leg[8],leg[9],leg[10],leg[11],leg[12],leg[13],leg[14],leg[15],leg[16],leg[17],leg[18],leg[19],leg[20],leg[21],leg[22],leg[23],leg[24],leg[25],leg[26],leg[27],leg[28],leg[29],leg[30],leg[31],leg[32],leg[33],leg[34],leg[35],leg[36],leg[37],leg[38],leg[39],leg[40],leg[41],leg[42],leg[43],leg[44],leg[45]])
        

        return response
        return super().form_valid(form)
    
class PDFExport(TemplateView):
    template_name = 'reports/importpastflighttimes.html'
    # form_class = DateSelector
    # success_url = '/reports/dates'

    def form_valid(self,form):
    #     userid=getuserid()
    #     if form['frombeginning'].value():
    #         startdate = True
    #     else:
    #         startdate = form['startdate'].value()

    #     if form['toend'].value():
    #         enddate = True
    #     else:
    #         enddate = form['enddate'].value()

    #     flights = callingdatabasedates(startdate,enddate,userid)

        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer)

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        p.drawString(100, 100, "Hello world.")

        # Close the PDF object cleanly, and we're done.
        p.showPage()
        p.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='hello.pdf')

class Export(FormView):
    template_name = 'reports/export.html'
    form_class = DateSelector
    success_url = '/reports'
    

    def get(self, request, *args, **kwargs):
        
        pagetitle = "Export Reports"

        return self.render_to_response({"title":pagetitle})

    def post(self, request, *args, **kwargs):
        userid=getuserid()
        if 'startall' in request.POST:
            startdate = True
        else:
            startdate = request.POST['startdate']
        
        if 'endall' in request.POST:
            enddate = True
        else:
            enddate = request.POST['enddate']
        
        flights = callingdatabasedates(startdate,enddate,userid)
        response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment;' f'filename="flighttime{startdate}-{enddate}.csv'},
    )

    
        writer = csv.writer(response)

        writer.writerow(['flightdate','aircraftId','departure','route','arrival','flightnum','deptime','offtime','ontime','arrtime','landings','imc','total','day','daylandings','night','nightlandings','printcomments','personalcomments','instructor','student','captain', 'firstofficer','flightattendants','passengercount','scheduleddeparttime','scheduledarrivaltime','scheduledblock','rotationid','aircrafttype','flighttime','distance'])
        for flight in flights:
            writer.writerow([flight.flightdate,flight.aircraftId,flight.departure,flight.route,flight.arrival,flight.flightnum,flight.deptime,flight.offtime,flight.ontime,flight.arrtime,flight.landings,flight.imc,flight.total,flight.day,flight.daylandings,flight.night,flight.nightlandings,flight.printcomments,flight.personalcomments,flight.instructor,flight.student,flight.captain,flight.firstofficer,flight.flightattendants,flight.passengercount,flight.scheduleddeparttime,flight.scheduledarrivaltime,flight.scheduledblock,flight.rotationid,flight.aircrafttype,flight.flighttime,flight.distance])
        

        return response


def exportflighttimeall(request):

    userid=getuserid()
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="flighttimeall.csv"'},
    )

    # flights = FlightTime.objects.filter(userid=userid).exclude(scheduledflight=True,deadheadflight=True)
    flights = FlightTime.objects.filter(userid=userid)
    writer = csv.writer(response)

    writer.writerow(['id','userid','flightdate','aircraftId','departure','route','arrival','flightnum','deptime','offtime','ontime','arrtime','landings','imc','hood','iap','typeofapproach','descriptionofapproach','holdnumber','holdboolean','pic','sic','cfi','dual','crosscountry','solo','total','day','daylandings','night','nightlandings','printcomments','personalcomments','ftd','ftdimc','sim','simimc','pcatd','pcimc','instructor','instructorid','student','studentid','captain', 'firstofficer','flightattendants','passengercount','scheduleddeparttime','scheduledarrivaltime','scheduledblock','rotationid','aircrafttype','flighttime','distance','scheduleddeparttimelocal','scheduledarrivaltimelocal','deptimelocal','offtimelocal','ontimelocal','arrtimelocal','reporttime','reporttimelocal','minutesunder','flightupdated','flightcreated','domestic','international','paycode','scheduledflight','deadheadflight','startdate','departuregate','arrivalgate','flightpath', 'airspeed','filedalt'])
    for flight in flights:
        writer.writerow([flight.id,flight.userid,flight.flightdate,flight.aircraftId,flight.departure,flight.route,flight.arrival,flight.flightnum,flight.deptime,flight.offtime,flight.ontime,flight.arrtime,flight.landings,flight.imc,flight.hood,flight.iap,flight.typeofapproach,flight.descriptionofapproach,flight.holdnumber,flight.holdboolean,flight.pic,flight.sic,flight.cfi,flight.dual,flight.crosscountry,flight.solo,flight.total,flight.day,flight.daylandings,flight.night,flight.nightlandings,flight.printcomments,flight.personalcomments,flight.ftd,flight.ftdimc,flight.sim,flight.simimc,flight.pcatd,flight.pcimc,flight.instructor,flight.instructorid,flight.student,flight.studentid,flight.captain, flight.firstofficer,flight.flightattendants,flight.passengercount,flight.scheduleddeparttime,flight.scheduledarrivaltime,flight.scheduledblock,flight.rotationid,flight.aircrafttype,flight.flighttime,flight.distance,flight.scheduleddeparttimelocal,flight.scheduledarrivaltimelocal,flight.deptimelocal,flight.offtimelocal,flight.ontimelocal,flight.arrtimelocal,flight.reporttime,flight.reporttimelocal,flight.minutesunder,flight.flightupdated,flight.flightcreated,flight.domestic,flight.international,flight.paycode,flight.scheduledflight,flight.deadheadflight,flight.startdate,flight.departuregate,flight.arrivalgate,flight.flightpath,flight.airspeed,flight.filedalt])
    

    return response


#editing the flightaware document. Just works on the local machine. Not 
# not designed for the website.
def editingFAdocument(request):
    currentuser = str(get_current_user())
    userid=User.objects.get(username=currentuser).pk
    filename = 'Master'
    preferences = Users.objects.filter(user_id=userid).values()
    with open('./logbook/fixtures/'+filename+'.csv','r') as read_file:
        logbook = csv.reader(read_file)
        notblank = []
        blank = []
        for flight in logbook:
            if flight[11] == '' or (flight[3] != flight[4] and flight[3] !='') or (flight[5]!=flight[6] and flight[5] !=''):
                blank.append(flight)
            else:
                notblank.append(flight)

        
    with open('./reports/fixtures/'+filename+'blank.csv','w') as outfile:
        write = csv.writer(outfile)
        write.writerows(blank)
    with open('./reports/fixtures/'+filename+'notblank.csv','w') as outfile:
        write = csv.writer(outfile)
        write.writerows(notblank)
    timenow = datetime.datetime.now().strftime("%H:%M")
    html = f"<html><body>Good to go. {timenow} </body></html>" 
    return HttpResponse(html)

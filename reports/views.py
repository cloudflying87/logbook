import os
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from aircraft.models import AircraftModel, Manufacture, NewPlaneMaster
from airport.views import airporthome
from logbook.models import FlightTime
from django.db.models.functions import ExtractYear
from user.models import Users
from django.contrib.auth.models import User
from django_currentuser.middleware import (
    get_current_user)
from user.views import getuserid
from django.core.paginator import Paginator
from django.db.models import Count,Sum,Avg
from django.db.models.functions import Round
from django.db.models import Q
import requests

@login_required(login_url='/')
def reporthome(request):
    print('hello')

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
class AirportLookup(TemplateView):
    template_name = 'reports/airportreport.html'
    
    def get(self, request, *args, **kwargs):
        airportcount = []
        pagetitle = "Airports"
        userid = getuserid()
        secondrequest = request.GET.get('lookup[id]')
        
        depart = FlightTime.objects.filter(Q(departure=secondrequest) | Q(arrival=secondrequest),userid=userid).exclude(Q(scheduledflight=1) | Q(total=0)).order_by('-flightdate')
        return self.render_to_response({'total':depart.count(),'depart':depart,"title":pagetitle})

#This is used to get the lookup page started


class CategoryDisplay(TemplateView):
    template_name = 'reports/categorydisplay.html'
    def get(self, request, *args, **kwargs):
        pagetitle = "Category Report"
        qs = []
        userid = getuserid()
        manufacture = Manufacture.objects.all().values()
        #this is used to get the category totals, you can also select the manufacture totals dropdown
        if request.GET.get('category') != None:
            id = request.GET.get('category')
            uniquetype = AircraftModel.objects.filter(mfr=id)
            for airtype in uniquetype:
                checkingfornone = FlightTime.objects.filter(userid=userid,aircrafttype=airtype).aggregate(Sum('total'))
                
                if checkingfornone['total__sum'] != None:
                    info = {'aircraftsummary': FlightTime.objects.filter(userid=userid,aircrafttype=airtype).aggregate(
                        airtotal = Sum('total'),
                        avgflight = Avg('total'),
                        numflight = Count('total'),
                        avgmiles = Avg('distance'),
                        totalmiles = Sum('distance'),
                        avgpax = Avg('passengercount'),
                        totalpax = Sum('passengercount'),
                        night = Sum('night'),
                        landings = Sum('landings'),
                    )}
                    #making it so that i can round the results the way I want
                    #them before appending them to the list to send them to the
                    #template in the context
                    record = {'aircraftype':airtype,'info':{'aircraftsummary':{'airtotal':info['aircraftsummary']['airtotal'],'avgflight':round((info['aircraftsummary']['avgflight']),2),'numflight':info['aircraftsummary']['numflight'],'avgmiles':int(round((info['aircraftsummary']['avgmiles']),0)),'totalmiles':info['aircraftsummary']['totalmiles'],'avgpax':int(round((info['aircraftsummary']['avgpax']),0)),'totalpax':info['aircraftsummary']['totalpax'],'night':info['aircraftsummary']['night'],'landings':info['aircraftsummary']['landings']}}}
                    if record['info']['aircraftsummary']['airtotal'] != None:
                        qs.append(record)
            tairtotal = 0; tavgflight = 0; tnumflight = 0; tavgmiles = 0
            ttotalmiles = 0; tavgpax = 0; ttotalpax = 0; count = 0; tnight = 0; tlandings = 0;
            #adding the totals for the categories
            for itemtotal in qs:
                tairtotal = tairtotal + (itemtotal['info']['aircraftsummary']['airtotal'])  
                tavgflight = tavgflight + (itemtotal['info']['aircraftsummary']['avgflight'])  
                tnumflight = tnumflight + (itemtotal['info']['aircraftsummary']['numflight'])  
                tavgmiles = tavgmiles + (itemtotal['info']['aircraftsummary']['avgmiles'])  
                ttotalmiles = ttotalmiles + (itemtotal['info']['aircraftsummary']['totalmiles'])  
                tavgpax = tavgpax + (itemtotal['info']['aircraftsummary']['avgpax'])  
                ttotalpax = ttotalpax + (itemtotal['info']['aircraftsummary']['totalpax'])  
                tnight = tnight + (itemtotal['info']['aircraftsummary']['night'])  
                tlandings = tlandings + (itemtotal['info']['aircraftsummary']['landings'])  
                count += 1
            
            record = {'aircraftype':'Total','info':{'aircraftsummary':{'airtotal':tairtotal,'avgflight':round((tavgflight/count),2),'numflight':tnumflight,'avgmiles':int((tavgmiles/count)),'totalmiles':ttotalmiles,'avgpax':int(tavgpax/count),'totalpax':ttotalpax,'night':tnight,'landings':tlandings}}}
            qs.append(record) 
            return self.render_to_response({"manufacture":manufacture,"qs":qs, "title":pagetitle})
        else:
            #gets all the airplanes
            uniquetype = FlightTime.objects.filter(userid=userid).values('aircrafttype').distinct()
            for airtype in uniquetype:
                info = {'aircraftsummary': FlightTime.objects.filter(userid=userid,aircrafttype=airtype['aircrafttype']).aggregate(
                    airtotal = Sum('total'),
                    avgflight = Avg('total'),
                    numflight = Count('total'),
                    avgmiles = Round(Avg('distance')),
                    totalmiles = Sum('distance'),
                    avgpax = Round(Avg('passengercount')),
                    totalpax = Sum('passengercount'),
                    night = Sum('night'),
                    landings = Sum('landings'),
                )}
                record = {'aircraftype':airtype['aircrafttype'],'info':{'aircraftsummary':{'airtotal':info['aircraftsummary']['airtotal'],'avgflight':round((info['aircraftsummary']['avgflight']),2),'numflight':info['aircraftsummary']['numflight'],'avgmiles':int(round((info['aircraftsummary']['avgmiles']),0)),'totalmiles':info['aircraftsummary']['totalmiles'],'avgpax':int(round((info['aircraftsummary']['avgpax']),0)),'totalpax':info['aircraftsummary']['totalpax'],'night':info['aircraftsummary']['night'],'landings':info['aircraftsummary']['landings']}}}
                
                if record['info']['aircraftsummary']['airtotal'] > 0:
                    qs.append(record)
            return self.render_to_response({"manufacture":manufacture,"qs":qs, "title":pagetitle})

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

class TailLookupDisplay(TemplateView):
    template_name = 'reports/taillookup.html'

    def get(self, request, *args, **kwargs):
        userid=getuserid()
        pagetitle = "Tail Number Lookup"
        secondrequest = request.GET.get('lookup[id]')

        info = FlightTime.objects.filter(userid=userid,aircraftId=secondrequest).aggregate(
                    airtotal = Sum('total'),
                    miletotal = Sum('distance'),
                    paxtotal = Sum('passengercount'),
                    flighttotal = Count('total'),
                    avgflight = Avg('total'),
                    avgdistance = Avg('distance'),
                    avgpax = Avg('passengercount')
            )
        flights = FlightTime.objects.filter(userid=userid,aircraftId=secondrequest).exclude(scheduledflight=True).order_by('-flightdate')
        
        return self.render_to_response({"title":pagetitle,"years":info,"depart":flights})

class FlightAware(TemplateView):
    template_name = 'reports/flightaware.html'

    def get(self, request, *args, **kwargs):
        
        pagetitle = "Flightaware API"
        
        ident = 'DAL2183'
        startdate = '2022-10-09'
        params = {"query": "start{startdate},"}
        endpoint = "https://aeroapi.flightaware.com/aeroapi/flights/{fident}"
        url = endpoint.format(fident=ident)
        
        headers = {'x-apikey': os.getenv('flightawareapi')}
        response = requests.get(url, headers=headers)
        print(response.json())
        if response.status_code == 200:  # SUCCESS
            result = response.json()
            result['success'] = True
        else:
            result['success'] = False
            if response.status_code == 404:  # NOT FOUND
                result['message'] = 'No entry found for "%s"' % ident
            else:
                result['message'] = 'Flightaware is currently not available'
        
        return self.render_to_response({"title":pagetitle,"info":result})

        
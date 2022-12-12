from django.contrib.auth.decorators import login_required
from django.views.generic import FormView, ListView
from aircraft.models import NewPlaneMaster,AircraftModel
from logbook.models import FlightTime
from user.views import getuserid
from dal import autocomplete
from aircraft.forms import AirplaneEntry
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic import FormView, DetailView
from django.views.generic.list import ListView
from aircraft.models import AircraftModel, Manufacture, NewPlaneMaster
from airport.views import airporthome
from logbook.models import FlightTime
from user.models import Users
from django.contrib.auth.models import User
from django_currentuser.middleware import (
    get_current_user)
from user.views import getuserid
from airline.views import flightaware
from django.core.paginator import Paginator
from django.db.models import Count,Sum,Avg
from django.db.models.functions import Round
from django.db.models import Q
from django.http import HttpResponse


@login_required(login_url='/')

def aircrafthome(request):
    print('hello')


class CategoryDisplayAll(TemplateView):
    template_name = 'aircraft/aircraftbase.html'
    def get(self, request, *args, **kwargs):
        pagetitle = "Category Report"
        qs = []
        userid = getuserid()
        manufacture = Manufacture.objects.all().values()
        #this is used to get the category totals, you can also select the manufacture totals dropdown
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
            lastflown = FlightTime.objects.filter(userid=userid,aircrafttype=airtype['aircrafttype']).exclude(scheduledflight=1).latest('flightdate')

            
            record = {'aircraftype':airtype['aircrafttype'],'info':{'aircraftsummary':{'airtotal':info['aircraftsummary']['airtotal'],'avgflight':round((info['aircraftsummary']['avgflight']),2),'numflight':info['aircraftsummary']['numflight'],'avgmiles':int(round((info['aircraftsummary']['avgmiles']),0)),'totalmiles':info['aircraftsummary']['totalmiles'],'avgpax':int(round((info['aircraftsummary']['avgpax']),0)),'totalpax':info['aircraftsummary']['totalpax'],'night':info['aircraftsummary']['night'],'landings':info['aircraftsummary']['landings']}},'lastflown':lastflown}
            
            if record['info']['aircraftsummary']['airtotal'] > 0:
                qs.append(record)
            
        return self.render_to_response({"manufacture":manufacture,"qs":qs, "title":pagetitle})
class CategoryDisplay(TemplateView):
    template_name = 'aircraft/categorydisplay.html'
    def get(self, request, *args, **kwargs):
        pagetitle = "Category Report"
        qs = []
        userid = getuserid()
        manufacture = Manufacture.objects.all().values()
        #this is used to get the category totals, you can also select the manufacture totals dropdown
    
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
                lastflown = FlightTime.objects.filter(userid=userid,aircrafttype=airtype).exclude(scheduledflight=1).latest('flightdate')
                
                #making it so that i can round the results the way I want
                #them before appending them to the list to send them to the
                #template in the context
                record = {'aircraftype':airtype,'info':{'aircraftsummary':{'airtotal':info['aircraftsummary']['airtotal'],'avgflight':round((info['aircraftsummary']['avgflight']),2),'numflight':info['aircraftsummary']['numflight'],'avgmiles':int(round((info['aircraftsummary']['avgmiles']),0)),'totalmiles':info['aircraftsummary']['totalmiles'],'avgpax':int(round((info['aircraftsummary']['avgpax']),0)),'totalpax':info['aircraftsummary']['totalpax'],'night':info['aircraftsummary']['night'],'landings':info['aircraftsummary']['landings']}},'lastflown':lastflown}
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
        
class TailBase(TemplateView):
    template_name = 'aircraft/tailbase.html'
    def get(self, request, *args, **kwargs):
        pagetitle = "Tail Number Lookup"
        return self.render_to_response({"title":pagetitle})
class TailLookupDisplay(TemplateView):
    template_name = 'aircraft/taillookup.html'

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
class TailNumberLookup(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = []
        userid = getuserid()
        disticttails = FlightTime.objects.filter(userid=userid).values('aircraftId').distinct().order_by('aircraftId')
        
        for aircraft in disticttails:
            data = {'id':aircraft['aircraftId'],'text':aircraft['aircraftId']}
            qs.append(data)
        
        # return  JsonResponse(correctdata, safe=False)
        # print(correctdata)
        # return self.render_to_response({"result":correctdata})
        qs = NewPlaneMaster.objects.all().order_by('nnumber')
        if self.q:
            qs = qs.filter(nnumber__istartswith=self.q)
        return qs


class NewIDLookup(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = AircraftModel.objects.all().order_by('type')
        if self.q:
            qs = qs.filter(type__istartswith=self.q)
        return qs
class AircraftEntry(FormView):
    
    template_name = 'aircraft/searchtype.html'
    form_class = AirplaneEntry
    success_url = 'entry'
    
    def form_valid(self,form):
        form.save()
        return super().form_valid(form)

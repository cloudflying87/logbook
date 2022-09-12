
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from aircraft.models import AircraftModel, Manufacture, NewPlaneMaster
from logbook.models import FlightTime
from user.models import Users
from django.contrib.auth.models import User
from django_currentuser.middleware import (
    get_current_user)
from user.views import getuserid
from django.core.paginator import Paginator
from django.db.models import Count,Sum,Avg
from django.db.models.functions import Round
from django.db.models import Q

@login_required(login_url='/')
def reporthome(request):
    print('hello')

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
                pax = Sum('passengercount')
            ),

            'totalflights': FlightTime.objects.all().filter(userid=userid).exclude(Q(scheduledflight=1) | Q(total=0)).aggregate(
            tflight = Count('flightdate'))}
        return self.render_to_response({"qs":qs, "title":pagetitle})

class CategoryDisplay(TemplateView):
    template_name = 'reports/categorydisplay.html'
    def get(self, request, *args, **kwargs):
        pagetitle = "Category Report"
        qs = []
        userid = getuserid()
        
        manufacture = Manufacture.objects.all()
        if request.GET.get('category') != None:
            id = Manufacture.objects.get(manufacture=request.GET.get('category')).pk
            print(id)
            uniquetype = AircraftModel.objects.filter(mfr=id)
            print(uniquetype)
            for airtype in uniquetype:
                print(airtype)
                info = {'aircraftsummary': FlightTime.objects.filter(userid=userid,aircrafttype=airtype).aggregate(
                    airtotal = Sum('total'),
                    avgflight = Avg('total'),
                    numflight = Count('total'),
                    avgmiles = Round(Avg('distance')),
                    totalmiles = Sum('distance'),
                    avgpax = Round(Avg('passengercount')),
                    totalpax = Sum('passengercount')
                )}
                record = {'aircraftype':airtype,'info':info}
                if record['info']['aircraftsummary']['airtotal'] != None:
                    qs.append(record)   
            return self.render_to_response({"manufacture":manufacture,"qs":qs, "title":pagetitle})
        else:
            uniquetype = FlightTime.objects.filter(userid=userid).values('aircrafttype').distinct()
            for airtype in uniquetype:
                info = {'aircraftsummary': FlightTime.objects.filter(userid=userid,aircrafttype=airtype['aircrafttype']).aggregate(
                    airtotal = Sum('total'),
                    avgflight = Avg('total'),
                    numflight = Count('total'),
                    avgmiles = Round(Avg('distance')),
                    totalmiles = Sum('distance'),
                    avgpax = Round(Avg('passengercount')),
                    totalpax = Sum('passengercount')
                )}
                record = {'aircraftype':airtype['aircrafttype'],'info':info}
                
                if record['info']['aircraftsummary']['airtotal'] > 0:
                    qs.append(record)
            return self.render_to_response({"manufacture":manufacture,"qs":qs, "title":pagetitle})

class Totals(ListView):
    
    model = FlightTime
    context_object_name = "flight"
    template_name = 'reports/basereport.html'
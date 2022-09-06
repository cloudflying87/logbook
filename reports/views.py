
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from aircraft.models import NewPlaneMaster
from logbook.models import FlightTime
from user.models import Users
from django.contrib.auth.models import User
from django_currentuser.middleware import (
    get_current_user)
from user.views import getuserid
from django.core.paginator import Paginator
from django.db.models import Count,Sum

@login_required(login_url='/')
def reporthome(request):
    print('hello')

class Totals(ListView):
    
    model = FlightTime
    context_object_name = "flight"
    template_name = 'reports/totals.html'

    def get_queryset(self):
        userid = getuserid()
        qs = {
            'total' : FlightTime.objects.all().filter(userid=userid).     aggregate(
                total = Sum('total'),
                day = Sum('day'),
                daylandings = Sum('daylandings'),
                night = Sum('night'),
                nightlandings = Sum('nightlandings'),
                totalflights = Count('flightdate')
            ),

            'totalflights': FlightTime.objects.all().filter(userid=userid).exclude(total=0).aggregate(
            tflight = Count('flightdate')
            ),
            '737800': FlightTime.objects.all().filter(userid=userid,aircrafttype = 'B737-800').exclude(total=0).aggregate(
                total = Sum('total')
                
            ),
        
        }
        
        return qs
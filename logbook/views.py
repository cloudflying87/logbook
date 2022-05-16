from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django_currentuser.middleware import (
    get_current_user)
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from airport.views import gettingairport
from aircraft.models import Master
import time
from airport.models import Airport
from django.urls import reverse_lazy
from dal import autocomplete
from .forms import FlightTimeEntry


class AirportAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Airport.objects.all()
        if self.q:
            qs = qs.filter(icao__istartswith=self.q)
        return qs

class AircraftIDLookup(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Master.objects.all()
        if self.q:
            qs = qs.filter(nnumber__istartswith=self.q)
        return qs

@login_required(login_url='/')
def logbookhome(request):
    print('hello')
class LogbookEntry(FormView):
    
    template_name = 'logbook/main.html'
    form_class = FlightTimeEntry
    success_url = 'entry'
    
    
    def form_valid(self,form):
        # print(form['arrtime'].value-form['deptime'].value)
        form.save()
        return super().form_valid(form)

def testairport(request):
    passingtime = time.time()
    icao = "KMSP"
    gatheredinfo = gettingairport(icao,passingtime)
    print(gatheredinfo)
    return render(request, 'logbook/main.html', {'gatheredinfo':gatheredinfo})
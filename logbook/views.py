from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from airport.views import gettingairport
import time
from airport.models import Airport
from dal import autocomplete
from .forms import FlightTimeEntry


class AirportAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Airport.objects.all()
        
        if self.q:
            qs = qs.filter(icao__istartswith=self.q)
        return qs

@login_required(login_url='/')
def logbookhome(request):
    if request.method == "POST":
        airlineForm = FlightTimeEntry(request.POST)
        # print(airlineForm['flightdate'])
        # print(airlineForm)
        if airlineForm.is_valid():
            
            airlineForm.userid=request.user.id
            # print(airlineForm[1])
            # print(airlineForm)
            # airlineForm.save()
    airlineForm = FlightTimeEntry()
    return render(request, 'logbook/main.html', {'airlineForm':airlineForm})

def testairport(request):
    passingtime = time.time()
    icao = "KMSP"
    gatheredinfo = gettingairport(icao,passingtime)
    print(gatheredinfo)
    return render(request, 'logbook/main.html', {'gatheredinfo':gatheredinfo})
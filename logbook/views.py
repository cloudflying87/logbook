from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from airport.views import gettingairport
import time
from .models import FlightTime
from .forms import FlightTimeEntry

@login_required(login_url='/')
def logbookhome(request):
    if request.method == "POST":
        airlineForm = FlightTimeEntry(request.POST)
        if airlineForm.is_valid():
            airlineForm.save()
    airlineForm = FlightTimeEntry()
    return render(request, 'logbook/main.html', {'airlineForm':airlineForm})

def testairport(request):
    passingtime = time.time()
    icao = "KMSP"
    gatheredinfo = gettingairport(icao,passingtime)
    print(gatheredinfo)
    return render(request, 'logbook/main.html', {'gatheredinfo':gatheredinfo})
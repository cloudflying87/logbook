from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from airport.views import gettingairport
from .models import Aircraftref, Engine, Master



@login_required(login_url='/')

def aircrafthome(request):
    
    return render(request, 'aircraft/searchtype.html', {})

def searchtype(request):
    
    if request.method == 'POST':
        aircraft_searched = request.POST['aircraft_searched']
        aircraftinfo = Master.objects.filter(nnumber=aircraft_searched).values('nnumber','serialnumber','mfrcode','engcode','yearmfr','airworthdate')
        
        typeinfo = Aircraftref.objects.filter(mfrcode = aircraftinfo[0]['mfrcode']).values('model','mfr','typeacft','typeengine','accat','numberseats','numberengines')

        
        enginecode = aircraftinfo[0]['engcode']
        engineinfo = Engine.objects.filter(engcode = enginecode).values('model','mfr','type','horsepower','thrust')
        return render(request, 'aircraft/displayresults.html', {'aircraftinfo':aircraftinfo[0],'engineinfo':engineinfo[0],'typeinfo':typeinfo[0]})
    else:
        return render(request, 'aircraft/searchtype.html', {})
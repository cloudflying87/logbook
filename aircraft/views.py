from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.shortcuts import render
from django.views.generic import FormView, ListView
from aircraft.models import NewPlaneMaster,AircraftModel
from logbook.models import FlightTime
from user.views import getuserid
from dal import autocomplete

from aircraft.forms import AirplaneEntry


@login_required(login_url='/')

def aircrafthome(request):
    print('hello')


# def tailnumberlookup(request):
#     correctdata = []
#     userid = getuserid()
#     disticttails = FlightTime.objects.filter(userid=userid).values('aircraftId').distinct().order_by('aircraftId')
    
#     for aircraft in disticttails:
        
#         data = {'id':aircraft['aircraftId'],'text':aircraft['aircraftId']}
#         correctdata.append(data)
#     print(correctdata)
#     # if self.q:
#     #     qs = qs.filter(type__istartswith=self.q)
#     return correctdata
class TailNumberLookup(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        userid = getuserid()
        qs = NewPlaneMaster.objects.all().order_by('nnumber')
        if self.q:
            qs = qs.filter(nnumber__istartswith=self.q)
        return qs


class NewIDLookup(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = AircraftModel.objects.all().order_by('type')
        if self.q:
            qs = qs.filter(type__istartswith=self.q)
            print(type(qs))
        return qs
class AircraftEntry(FormView):
    
    template_name = 'aircraft/searchtype.html'
    form_class = AirplaneEntry
    success_url = 'entry'
    
    def form_valid(self,form):
        form.save()
        return super().form_valid(form)

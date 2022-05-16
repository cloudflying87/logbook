from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Aircraftref, Engine, Master
from .forms import AirplaneEntry
from django.views.generic import FormView
from dal import autocomplete

class ModelIDLookup(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Aircraftref.objects.all().order_by('mfrcode')
        if self.q:
            qs = qs.filter(model__istartswith=self.q)
            print(qs)
        return qs

@login_required(login_url='/')

def aircrafthome(request):
    
    return render(request, 'aircraft/searchtype.html', {})

class AirplaneSearch(FormView):
    
    template_name = 'aircraft/searchtype.html'
    form_class = AirplaneEntry
    success_url = 'modellookup'
    
    
    def form_valid(self,form):
        print(form)
        # form.save()
        return super().form_valid(form)
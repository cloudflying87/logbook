from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.shortcuts import render
from django.views.generic import FormView
from aircraft.models import NewPlaneMaster,AircraftModel
from dal import autocomplete

from aircraft.forms import AirplaneEntry


@login_required(login_url='/')

def aircrafthome(request):
    print('hello')
class NewIDLookup(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = AircraftModel.objects.all().order_by('type')
        if self.q:
            qs = qs.filter(nnumber__istartswith=self.q)
            print(type(qs))
        return qs
class AircraftEntry(FormView):
    
    template_name = 'aircraft/searchtype.html'
    form_class = AirplaneEntry
    success_url = 'entry'

    def get(self, *args, **kwargs):
        pagetitle = "Test"
        formset = formset_factory(AirplaneEntry)
        return self.render_to_response({'transaction_formset':formset})
    
    def form_valid(self,form):
        form.save()
        return super().form_valid(form)

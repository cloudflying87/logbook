from django import forms
# from django.db.models.fields import Field
from django.forms import widgets
from django.forms.widgets import DateInput
from logbook.models import FlightTime
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from django_currentuser.middleware import (
    get_current_user)
from dal import autocomplete


class AirplaneEntry(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(AirplaneEntry,self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['aircraftId'].label = "Tail Number"
        self.fields['aircraftId'].initial = 'N102NB'
        
    class Meta:
        model = FlightTime
        fields = ('aircraftId',)
        widgets = {
            'aircraftId':autocomplete.ModelSelect2(url='aircraftidlookup'),
        }
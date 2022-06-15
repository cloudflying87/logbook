from django import forms
from django.urls import reverse_lazy
# from django.db.models.fields import Field
from .models import NewPlaneMaster
from crispy_forms.helper import FormHelper
from django_currentuser.middleware import (
    get_current_user)
from dal import autocomplete


class AirplaneEntry(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(AirplaneEntry,self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        
        self.fields['nnumber'].label = "Tail Number"
        self.fields['nnumber'].initial = 'N102NB' 
    class Meta:
        model = NewPlaneMaster
        fields = ('nnumber',)
        widgets = {
            'nnumber':autocomplete.Select2(url=('aircraftidlookup')),
        }
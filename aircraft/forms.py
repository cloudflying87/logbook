from django import forms
# from django.db.models.fields import Field
from django.forms import widgets
from django.forms.widgets import DateInput
from aircraft.models import NewPlaneMaster
from logbook.models import FlightTime
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from django_currentuser.middleware import (
    get_current_user)
from dal import autocomplete
# from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField
# from ajax_select import make_ajax_field

class AirplaneEntry(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(AirplaneEntry,self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['aircraftmodel'].label = "Model"
        self.fields['aircraftmodel'].initial = 'B737-900'
        
    class Meta:
        model = NewPlaneMaster
        fields = ('aircraftmodel',)
        # widgets = {
        #     'aircraftmodel':autocomplete.ModelSelect2(url='newidlookup'),
        # }



# class AirplaneEntry(forms.ModelForm):

#     def __init__(self, *args, **kwargs):
#         super(AirplaneEntry,self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.fields['aircraftmodel'].label = "Model"
#         self.fields['aircraftmodel'].initial = 'B737-900'
#     class Meta:
#         model = NewPlaneMaster
#         fields = ('aircraftmodel',)

#         # aircraftmodel = make_ajax_field(NewPlaneMaster, 'nnumber', 'aircraftid', help_text=None)
#         aircraftmodel = AutoCompleteSelectField('nnumber', required=False, help_text=None)
#         # tags = AutoCompleteSelectMultipleField('tags', required=False, help_text=None)
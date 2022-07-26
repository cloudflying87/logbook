from multiprocessing import get_context
from django import forms
# from django.db.models.fields import Field
from django.forms import widgets
from django.forms.widgets import DateInput
from user.models import Users
from .models import FlightTime
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from django_currentuser.middleware import (
    get_current_user)
from crispy_forms.layout import Layout, Submit, Row, Column,Fieldset,Field
from airport.models import Airport
from dal import autocomplete


class FlightTimeEntry(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FlightTimeEntry,self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        currentuser = str(get_current_user())
        userid=User.objects.get(username=currentuser).pk
        preferences = Users.objects.filter(user_id=userid).values()
        pic = preferences[0]['pic']
        sic = preferences[0]['sic']
        self.initial['userid'] = userid
        self.fields['flightdate'].label = "Date"
        self.fields['aircraftId'].label = "Tail Number"
        self.fields['aircraftId'].initial = 'N102NB'
        self.fields['deptime'].initial = "11:00"
        self.fields['departure'].label = "Departure Airport"
        self.fields['arrival'].label = "Arrival Airport"
        self.fields['flightnum'].label = "Flight Number"
        self.fields['deptime'].label = "Departure Time (Out)"
        self.fields['offtime'].label = "Take-off Time(Off)"
        self.fields['ontime'].label = "Landing Time(On)"
        self.fields['arrtime'].label = "Arrival Time(In)"
        self.fields['imc'].label = "Instrument"
        self.fields['passengercount'].label = "Pax Count"
        self.fields['iap'].label = "Number of Approaches"
        self.fields['typeofapproach'].label = "Type of Approach"
        self.fields['printcomments'].label = "Comments for Print Logbook"
        self.fields['personalcomments'].label = "Comments - For Personal Memories"
        

        if pic:
            self.fields['firstofficer'].label = 'First Officer'
            self.fields['captain'].widget = forms.HiddenInput()
        
        if sic:
            self.fields['firstofficer'].widget = forms.HiddenInput()
            self.fields['captain'].label = 'Captain'
        

        self.helper.layout = Layout(
            Fieldset(
                'Flight entry form',
                Field('userid',type='hidden'),
                Row(
                    'aircraftId',
                    Column(Field('flightdate',type='date'),css_class='form-group col-sm-3 mb-1'),
                    Column('departure',css_class='form-group col-sm-3 mb-1'),
                    Column('arrival',css_class='form-group col-sm-3 mb-1'),
                    Column('flightnum',css_class='form-group col-sm-3 mb-1', wrapper_class='extra-class')
                    ),
                Row(
                    'deptime',
                    'offtime',
                    'ontime',
                    'arrtime',
                ),
                Row(
                    'landings',
                    'imc',
                    'passengercount',
                    'iap',
                    'typeofapproach',
                ),
                'firstofficer',
                'captain',
                'printcomments',
                'personalcomments',
                
                
            ),
           Submit('Submit', 'Save')
           
        )

        
    class Meta:
        model = FlightTime
        fields = ('userid','aircraftId','flightdate','departure','arrival','flightnum','deptime','offtime','ontime','arrtime','landings','printcomments','personalcomments','imc','passengercount','iap','typeofapproach','total','captain','firstofficer' )
        widgets = {
            # 'aircraftId':autocomplete.ModelSelect2(url='aircraftidlookup'),
            # 'departure':autocomplete.ModelSelect2(url='autocomplete'),
            # 'arrival':autocomplete.ModelSelect2(url='autocomplete'),
            'flightdate': DateInput(attrs={'type': 'date'}),
        }
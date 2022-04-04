from django import forms
# from django.db.models.fields import Field
from django.forms import widgets
from .models import FlightTime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column,Fieldset,Field
from airport.models import Airport
from dal import autocomplete


class FlightTimeEntry(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Flight entry form',
                Field('userid',type='hidden'),
                Row(
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
                    'passengercount'
                ),
                
                'printcomments',
                'personalcomments',
            ),
           (Submit('Submit', 'save'))
        )
    class Meta:
        model = FlightTime
        fields = ('userid','flightdate','departure','arrival','flightnum','deptime','offtime','ontime','arrtime','landings','printcomments','personalcomments','imc','passengercount' )
        widgets = {
            'departure':autocomplete.ModelSelect2(url='autocomplete'),
            'arrival':autocomplete.ModelSelect2(url='autocomplete'),
        }
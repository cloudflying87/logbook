from cProfile import label
from django import forms
# from django.db.models.fields import Field
from django.forms import widgets
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column,Fieldset,Field
from .models import Master, Aircraftref, Engine
from dal import autocomplete

class AirplaneEntry(forms.Form):
    Nnumber = forms.CharField(label='Tail Number',max_length = 7)
    typeaircraft = forms.CharField(label='Aircraft Type',)
    #widget=autocomplete.ModelSelect2(url='modellookup'))
    
        
        
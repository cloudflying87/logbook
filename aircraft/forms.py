from cProfile import label
from django import forms
# from django.db.models.fields import Field
from dal import autocomplete

class AirplaneEntry(forms.Form):
    Nnumber = forms.CharField(label='Tail Number',max_length = 7)
    typeaircraft = forms.CharField(label='Aircraft Type',)
    
    
        
        
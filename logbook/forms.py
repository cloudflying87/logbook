from django import forms
from .models import FlightTime


class FlightTimeEntry(forms.ModelForm):

    class Meta:
        model = FlightTime
        fields = ('flightdate','departure','arrival','flightnum','deptime','offtime','ontime','arrtime','landings','printcomments','personalcomments','imc' )
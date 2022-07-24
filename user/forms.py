from django import forms
from django.forms import widgets
from .models import Users
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from django_currentuser.middleware import (
    get_current_user)
from crispy_forms.layout import Layout, Submit, Row, Column,Fieldset,Field
from airport.models import Airport
from dal import autocomplete


class UserPreferences(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(UserPreferences,self).__init__(*args, **kwargs)
    
    class Meta:
        model = Users
        fields = ('pic','sic','cfi','dual','solo','cx','decimal','time','decimalplaces','defaultairport','defaultairplane','airlineform','zulu')
        
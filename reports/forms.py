
from django import forms
from django.forms.widgets import DateInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row,Fieldset,Field


class DateSelector(forms.Form):
    
    startdate = forms.DateField(
        label='Start Date',
        widget=DateInput(attrs={'type': 'date'}),
        required=False)
    frombeginning = forms.BooleanField(
        label="From Beginning",
        required=False)
    enddate = forms.DateField(
        label='End Date',
        widget=DateInput(attrs={'type': 'date'}),
        required=False)
    toend = forms.BooleanField(
        label='To End',
        required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-dateSelector'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Date Selector',
                'startdate',
                'frombeginning',
                Field('enddate',type='date'),
                'toend'
            ),
            Submit('Submit', 'Lookup')
        )
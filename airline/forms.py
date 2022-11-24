from crispy_forms.helper import FormHelper
from django import forms
from tinymce.widgets import TinyMCE
from airline.models import Rotations
from crispy_forms.layout import Layout, Submit, Row, Column,Fieldset,Field

class AirlineScheduleEntry(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(AirlineScheduleEntry,self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['rawdata'].label = "Paste Schedule"
        
        self.helper.layout = Layout(
            Fieldset(
                'Schedule entry form',
                'airline',
                'rotationid',
                'rawdata',
            ),
            Submit('Submit', 'Save')
        )

    class Meta:
        model = Rotations
        fields = ('rawdata','airline','rotationid')
        widgets = {
            'rawdata':TinyMCE(attrs={'cols': 80, 'rows': 30})

        }
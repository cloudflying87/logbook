from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import FormView
from dal import autocomplete


@login_required(login_url='/')

def aircrafthome(request):
    
    return render(request, 'aircraft/searchtype.html', {})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from aircraft.models import NewPlaneMaster
from airport.models import Airport
import logbook.models
from dal import autocomplete
from user.models import Users
from django.contrib.auth.models import User
from django_currentuser.middleware import (
    get_current_user)

from django.core.paginator import Paginator

@login_required(login_url='/')
def reporthome(request):
    print('hello')


def logbookdisply(request):
    currentuser = str(get_current_user())
    userid=User.objects.get(username=currentuser).pk
    
    logbookdisplay = logbook.models.FlightTime.objects.all().filter(userid=userid).order_by('flightdate')
    entries = Paginator(logbookdisplay,25)

    # getting the desired page number from url
    page_number = request.GET.get('page')
    # try:
    page_obj = entries.get_page(page_number)  # returns the desired page object
    # except PageNotAnInteger:
    #     # if page_number is not an integer then assign the first page
    #     page_obj = entries.page(1)
    # except EmptyPage:
    #     # if page is empty then return last page
    #     page_obj = entries.page(entries.num_pages)
    context = {'page_obj': page_obj}
    # sending the page object to index.html
    # return render(request, 'index.html', context)

    return render(request,'reports/logbook.html',{'logbookdisplay':page_obj}) 
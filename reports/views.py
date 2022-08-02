
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



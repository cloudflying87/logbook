from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import UpdateView

from user.models import Users
from .forms import UserPreferences

# def home(request):
#     return render(request, 'user/signin.html', {})

def login_user(request):
    if request.method =="POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('logbookdisplay')
        else:
            messages.success(request, "Incorrect username or password.")
            return redirect('/')

    else:
        return render(request, 'user/signin.html', {})

def create_user(request):
    return render(request, 'user/signup.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, "You logged out successfully")
    return redirect('/')

class UpdatePreferences(UpdateView):
    
    model=Users
    template_name = 'user/updatepreferences.html'
    form_class = UserPreferences
    
    success_url = 'updatepreferences'
    
    def form_valid(self,form):
        form.save()
        return super().form_valid(form)
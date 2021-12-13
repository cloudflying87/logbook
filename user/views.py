from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

# def home(request):
#     return render(request, 'user/signin.html', {})

def login_user(request):
    if request.method =="POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('logbookhome')
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
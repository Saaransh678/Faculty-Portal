from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import LoginForm
from django.contrib import messages
from django.http import HttpResponse
from login_app.models import Faculty, activeleaveentries
# Create your views here.
def index(request):
    print(request.user)
    if request.user.is_anonymous:
        return redirect('/login')
    return render(request,"logined.html")

def login_req(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if form.cleaned_data['is_cross'] == True:
                # Special Permissions Processing
                print("Super")

            else:
                user = authenticate(username=username, password=password)

                if user is not None:
                    login(request, user)
                    return redirect("/")

                else:
                    messages.error(request, "Failed Login!! :' (")
                    return HttpResponse("Incorrect Username/Pass")

            # Check Later
                # Incorrect credentials, let's throw an error to the screen.
                # return render(request, 'ecommerce/user/login.html', {'error_message': 'Incorrect username and / or password.'})

        else:
            print(form.errors)
            return HttpResponse("Invalid Form, Check Error")

    return render(request=request, template_name="loginpage.html")
def logoutuser(request):
    logout(request)
    return redirect("/login")
def profile(request):
    return render(request=request, template_name="profile.html")
def application(request):
    return render(request=request, template_name="application.html")
def status(request):
    actv= activeleaveentries.objects.all()
    return render(request=request, template_name="status.html",context={'atv':actv})
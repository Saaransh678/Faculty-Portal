from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib import messages
from django.http import HttpResponse

# Create your views here.


def login_req(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                messages.success(request, "SuccesFul Login!!")
                print("SuccesFul Login!!")
                return HttpResponse("SuccesFul Login, Home page Here")
                # Save session as cookie to login the user
                # login(request, user)
                # Success, now let's login the user.
                # return render(request, '/main/register')
            else:
                messages.error(request, "Failed Login!! :' (")
                return HttpResponse("Incorrect Username/Pass")
            # Incorrect credentials, let's throw an error to the screen.
            # return render(request, 'ecommerce/user/login.html', {'error_message': 'Incorrect username and / or password.'})
        else:
            print(form.errors)
            return HttpResponse("Invalid Form")

    else:
        return render(request=request, template_name="loginpage.html")

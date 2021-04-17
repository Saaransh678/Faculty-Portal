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
            print(request.POST)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if form.cleaned_data['is_cross'] == True:
                # Special Permissions Processing
                print("Super")

            else:
                user = authenticate(username=username, password=password)

                if user is not None:
                    print("SuccesFul Login!!")
                    login(request, user)
                    messages.success(request, "SuccesFul Login!!")
                    return HttpResponse("SuccesFul Login, Home page Here")

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

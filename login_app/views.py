from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import LoginForm
from django.contrib import messages
from django.http import HttpResponse
from login_app.models import Faculty, activeleaveentries
from main.models import Faculty
# Create your views here.

departments = {'EE': 'Electrical',
               'ME': 'Mechanical', 'CSE': 'Computer Science'}

levels = ['Faculty', 'Head of Department', 'Dean Faculty Affairs', 'Director']


def index(request):
    # print(request.user)
    if request.user.is_anonymous:
        return redirect('/login')

    return redirect('/profile')


def login_req(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            print(request.POST)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # if form.cleaned_data['is_cross'] == True:
            #     # Special Permissions Processing
            #     print("Super")

            user = authenticate(username=username, password=password)

            if user is not None:
                messages.success(
                    request, f"Welcome back, {user.first_name}!!")
                login(request, user)
                return redirect("/profile")

            else:
                messages.error(
                    request, "Failed Login!! :'( Please Check Username/Password")

        else:
            print(form.errors)
            messages.error(
                request, "Unexpected Error!! Try Refreshing the page")

    return render(request=request, template_name="loginpage.html")


def logoutuser(request):
    logout(request)
    return redirect("/login")


def profile(request):
    user = request.user
    fullname = user.first_name + " " + user.last_name

    querry = f'SELECT * FROM main_faculty WHERE \"FacultyID\" ={user.id}'
    context_dict = {'email': user.email,
                    'name': fullname, 'uname': user.username}
    for faculty_details in Faculty.objects.raw(querry):
        context_dict['dept'] = departments[faculty_details.dept] + \
            " Department"
        context_dict['rem_leave'] = faculty_details.leaves_remaining
        context_dict['perm'] = levels[faculty_details.permission_level]

    return render(request=request, template_name="profile.html", context=context_dict)


def application(request):
    return render(request=request, template_name="application.html")


def status(request):
    actv = activeleaveentries.objects.all()
    return render(request=request, template_name="status.html", context={'atv': actv})

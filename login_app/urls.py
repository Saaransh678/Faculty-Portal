from django.contrib import admin
from django.urls import path
from django.urls import path, include
from . import views
from django.shortcuts import render, redirect
from django.http import HttpResponse
from pymongo import MongoClient
from .forms import ProfileChangeForm


def mongo_funct(request):
    client = MongoClient(
        'mongodb+srv://admin_0:pass1234@cluster0.2449b.mongodb.net/dbms?retryWrites=true&w=majority')
    db = client.dbms
    col = db.publication_details
    outp_ob = col.find()
    print(outp_ob[0])
    return HttpResponse(str(outp_ob[0]))


def url_par(request, id):
    client = MongoClient(
        'mongodb+srv://admin_0:pass1234@cluster0.2449b.mongodb.net/dbms?retryWrites=true&w=majority')
    db = client.dbms
    col = db.Data
    outp_ob = col.find_one({"fac_id": id})

    return HttpResponse(str(outp_ob))


def tryJson(request):
    if request.method == "POST":
        form = ProfileChangeForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            print(form.cleaned_data['json'])
            print(form.cleaned_data['json']['a'])
        else:
            print(form.errors)
    new_form = ProfileChangeForm()
    return render(request=request, template_name="trial.html", context={"form": new_form})


urlpatterns = [
    # path('', views.login_req),
    path('', views.index),
    path('profiles/id=<int:id>', url_par, name="faculty_details"),
    path('login/', views.login_req, name="login"),
    path('logout/', views.logoutuser, name="logout"),
    path('profile/', views.profile, name="profile"),
    path('application/', views.application, name="application"),
    path('status/', views.status, name="status"),
    path('requests/', views.requests, name="requests"),
    path('appointment/', views.appointment, name="appointment"),
    path('mongo_sample/', mongo_funct, name="sample_retreive_mongo"),
    path('trial/', tryJson),
]

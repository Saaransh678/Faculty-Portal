from django.contrib import admin
from django.urls import path
from django.urls import path, include
from . import views
from django.shortcuts import render, redirect
from django.http import HttpResponse
from pymongo import MongoClient


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


def redir(request):
    if request.user.is_anonymous:
        return redirect('/login')
    return redirect(f'/profile/id={request.user.id}')


urlpatterns = [
    # path('', views.login_req),
    path('', views.index),
    path('profiles/id=<int:id>', url_par, name="faculty_details"),
    path('login/', views.login_req, name="login"),
    path('logout/', views.logoutuser, name="logout"),
    path('profile/id=<int:req_id>', views.profile, name="profile"),
    path('profile/', redir),
    path('application/', views.application, name="application"),
    path('status/', views.status, name="status"),
    path('requests/', views.requests, name="requests"),
    path('appointment/', views.appointment, name="appointment"),
    path('mongo_sample/', mongo_funct, name="sample_retreive_mongo"),
]

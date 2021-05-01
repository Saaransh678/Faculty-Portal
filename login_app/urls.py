from django.contrib import admin
from django.urls import path
from django.urls import path, include
from . import views

from django.http import HttpResponse
from pymongo import MongoClient


def mongo_funct(request):
    client = MongoClient(
        'mongodb+srv://admin_0:pass1234@cluster0.2449b.mongodb.net/dbms?retryWrites=true&w=majority')
    db = client.dbms
    col = db.publication_details
    outp_ob = col.find()
    return HttpResponse(str(outp_ob))


urlpatterns = [
    # path('', views.login_req),
    path('', views.index),
    path('login/', views.login_req, name="login"),
    path('logout/', views.logoutuser, name="logout"),
    path('profile/', views.profile, name="profile"),
    path('application/', views.application, name="application"),
    path('status/', views.status, name="status"),
    path('requests/', views.requests, name="requests"),
    path('appointment/', views.appointment, name="appointment"),
    path('mongo_sample/', mongo_funct, name="sample_retreive_mogno"),
]

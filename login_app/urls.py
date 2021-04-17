from django.contrib import admin
from django.urls import path
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index),
    path('login/',views.login_req,name="login"),
    path('logout/',views.logoutuser,name="logout"),
     path('profile/',views.profile,name="profile"),
     path('application/',views.application,name="application"),
    path('status/',views.status,name="status"),
]

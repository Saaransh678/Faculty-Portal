"""Faculty_Portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from django.views.generic.base import RedirectView

from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from .views import base_page
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.apps import apps
import django
from main.models import Comments


def sample_funct(request):
    all_fields = Comments._meta.fields
    string = ""
    for val in all_fields:
        string += str(val).split(".")[-1] + ", "
    return HttpResponse(string)


def set_pass(request):
    user_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

    usernames = ['fqF5zTtE8l', 'RRHGiynHEH', '66E9cozk0i', 'haT5tOIlyS', 'T4hWpnBjAb', 'zdAqmw5bXL', 'VvuNypIEem', 'aB1umpsFsU', 'MkGPsikwrn', 'bkdDx2eqlt', 'GYPGKz6Bk8', 'AYQnEkZZIn',
                 '8Kom3Hdzlf', 'pS9hlqS2ot', 'Lc3RU6krLk', 'JpSxPfJkTg', 'aAQuTHT1tw', 'AklrHg11VL', 'URM1rZxLee', 'c2T61xfwDk', 'hod_cse', 'hod_ee', 'hod_me', 'dean_aa', 'director']

    passwords = ['ruZIze93l3', '58FeMvtFRP', 'VJWrluHjUx', 'lQvWLY47iw', 'DOROHtTB2M', 'ENxZgsML5J', 'sQE4HtaLN1', 'l8hTn79A4e', 'KOkFaEyVWo', 'UmBDatAwpd', '4gEcLxfoLx', 'gsr56632aj',
                 '748qkBy7Kn', 'zOT4EhzRD4', '1SIyhcIbJu', 'dxpVL9awVG', 'V89xtrgR0X', 'Js1nIzSwOl', 'ClYKUC9nwZ', 'T8QvqH3zXg', 'wOWUr750Cl', 's7IdGxZhaw', 'XN70Xhwo8A', 'P2mBCOi1zV', 'TAnrcEjrlj']

    for i in range(len(user_ids)):
        user_id, password = (user_ids[i], passwords[i])
        u = User.objects.get(id=user_id)
        if u is not None:
            u.set_password(password)
            u.save()

    return HttpResponse("Resetted Passwords")


def list_apps(request):
    # save = "Login_App, Administration, Authentication and Authorization, Content Types, Sessions, Messages, Static Files, Crispy_Forms, "
    app_names = ""
    # app_list = ['main', 'login_app']
    # django.apps.apps.populate(installed_apps=app_list)
    # django.apps.apps.set_available_apps(['main'])
    for app in apps.get_app_configs():
        app_names += app.verbose_name + ", "
        print(app.verbose_name)
    return HttpResponse(app_names)


def deleteAll(request):
    User.objects.all().delete()
    return HttpResponse("WARNING SAB UDD GYA")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('main/', include('main.urls')),
    path('check/', sample_funct),
    path('', include('login_app.urls')),
    path('favicon.ico', RedirectView.as_view(
        url=staticfiles_storage.url('images/favicon.ico'))),
    path('set_pass/', set_pass),
    path('list_apps/', list_apps),
    # path('deleteAll/', deleteAll)
]

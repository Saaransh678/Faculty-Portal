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
# from main.models import Comments, Previous_Record
from django.db import connections


def sample_funct(request):
    # all_fields = Previous_Record._meta.fields
    all_fields = ""
    string = ""
    for val in all_fields:
        string += str(val).split(".")[-1] + ", "
    return HttpResponse(string)


def set_pass(request):
    user_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

    # usernames = ['fqF5zTtE8l', 'RRHGiynHEH', '66E9cozk0i', 'haT5tOIlyS', 'T4hWpnBjAb', 'zdAqmw5bXL', 'VvuNypIEem', 'aB1umpsFsU', 'MkGPsikwrn', 'bkdDx2eqlt', 'GYPGKz6Bk8', 'AYQnEkZZIn',
    #              '8Kom3Hdzlf', 'pS9hlqS2ot', 'Lc3RU6krLk', 'JpSxPfJkTg', 'aAQuTHT1tw', 'AklrHg11VL', 'URM1rZxLee', 'c2T61xfwDk', 'hod_cse', 'hod_ee', 'hod_me', 'dean_aa', 'director']

    # passwords = ['ruZIze93l3', '58FeMvtFRP', 'VJWrluHjUx', 'lQvWLY47iw', 'DOROHtTB2M', 'ENxZgsML5J', 'sQE4HtaLN1', 'l8hTn79A4e', 'KOkFaEyVWo', 'UmBDatAwpd', '4gEcLxfoLx', 'gsr56632aj',
    #              '748qkBy7Kn', 'zOT4EhzRD4', '1SIyhcIbJu', 'dxpVL9awVG', 'V89xtrgR0X', 'Js1nIzSwOl', 'ClYKUC9nwZ', 'T8QvqH3zXg', 'wOWUr750Cl', 's7IdGxZhaw', 'XN70Xhwo8A', 'P2mBCOi1zV', 'TAnrcEjrlj']
    passwords = ['dnX48G4hSj', 'lldKDgAZO6', 'h41D7RF6t9', 'NtqjtNkqVR', 'NomUtfbAUu', 'm1kxmGUQFh', 'qm9oiPKCIx', 'D1baeB7BCX', 'TuEfJELEma', 'J0H2BIv7oz', 'SbkW6Inore', 'VZS2Q9rZUK',
                 'lNrSvd4MzX', 'HVOOjSV1aZ', 'Hv0FOEWsqV', '14MJwRwuFp', 'V2OUud1xMT', 'aDJ6IWPr6z', 'gddRaqLT4V', 'E6zNeDEWks', 'eedwX9shQZ', '1KF18PUQ6n', '5o60bNiWbP', '8qYuR4LVZP', 'dB3qeY2Fmj']

    usernames = ['director', 'dean_aa', 'hod_cse', 'hod_ee', 'hod_me', 'JQHyfvOfvr', 'D8g3iRMLyJ', 'vHr67qPsx1', 'nRidm5may1', 'Z7wLQnbctM', 'JnKITDyjFC', 'zhGNmvwDFC', 'Y6USVuUTsp',
                 'tHxJO0JKtR', 'U15xCM5sSK', 'cDc9tcNr2U', 'gluxCLBZKD', '9EyUQIJ6R9', 'hiS9cpNL3X', 'fIFZfKPKVy', 'B7tSQgSjGz', 'b3CmGnAUdb', 'O8rGCrgna1', 'hHHdHbKQRY', 'F5Z1bDK78W']

    for i in range(len(user_ids)):
        user_id, password = (usernames[i], passwords[i])
        u = User.objects.get(username=user_id)
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
    # path('check/', sample_funct),
    path('', include('login_app.urls')),
    path('favicon.ico', RedirectView.as_view(
        url=staticfiles_storage.url('images/favicon.ico'))),
    path('set_pass/', set_pass),
    path('list_apps/', list_apps),

    # path('deleteAll/', deleteAll)
]

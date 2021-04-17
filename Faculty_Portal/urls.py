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


def set_pass(request):
    user_ids = [100, 101]
    password = ['some_pass112', 'another_pass2345']

    for i in range(len(user_ids)):
        user_id, password = (user_ids[i], password[i])
        u = User.objects.get(id=user_id)
        if u is not None:
            u.set_password(password)
            u.save()

        return HttpResponse("Resetted Passwords")


urlpatterns = [
    path('', base_page),
    path('admin/', admin.site.urls),
    path('main/', include('main.urls')),
    path('login/', include('login_app.urls')),
    path('favicon.ico', RedirectView.as_view(
        url=staticfiles_storage.url('images/favicon.ico'))),
    path('set_pass/', set_pass),
]

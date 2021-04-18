from django.urls import path, include
from . import views
from .models import Active_Leave_Entries, Comments


urlpatterns = [
    path('', views.sample_render),
    path('register', views.register_request, name="register")

]

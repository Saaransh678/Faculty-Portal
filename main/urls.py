from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index),
    path('register', views.register_request, name="register")
    # path('new', views.new_prod)
]

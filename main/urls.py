from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.sample_render),
    path('register', views.register_request, name="register")
    # path('new', views.new_prod)
]

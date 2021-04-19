from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(label='username')
    password = forms.CharField(widget=forms.PasswordInput)
    is_cross = forms.BooleanField(initial=False, required=False)

    # class Meta:
    #     model = User
    #     fields = ("username", "email", "password1", "password2")


class NewApplicationForm(forms.Form):
    startdate = forms.DateField()
    enddate = forms.DateField()
    description = forms.CharField(max_length=300)
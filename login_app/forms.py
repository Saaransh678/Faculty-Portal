from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(label='username')
    password = forms.CharField(widget=forms.PasswordInput)
    is_cross = forms.BooleanField(initial=False, required=False)


class NewApplicationForm(forms.Form):
    startdate = forms.DateField()
    enddate = forms.DateField()
    description = forms.CharField(max_length=300)


class RequestForm(forms.Form):
    comments = forms.CharField(max_length=300)
    faculty_id = forms.IntegerField()
    verdict = forms.ChoiceField(
        choices=((0, 0), (1, 1,), (2, 2)), widget=forms.RadioSelect)


class ResponseForm(forms.Form):
    comments = forms.CharField(max_length=300)
    entryid = forms.IntegerField()

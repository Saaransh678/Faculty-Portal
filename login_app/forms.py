from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# from splitjson.widgets import SplitJSONWidget


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


class AppointmentForm(forms.Form):
    post_id = forms.IntegerField()
    new_fac_id = forms.IntegerField()


class NewCourseForm(forms.Form):
    course_code = forms.CharField(max_length=10)
    course_name = forms.CharField(max_length=200)


class NewPublicationForm(forms.Form):
    authors = forms.CharField(max_length=300)
    journal_name = forms.CharField(max_length=300)
    year = forms.IntegerField()


class bgform(forms.Form):
    desc = forms.CharField(max_length=400)


class PublicationForm(forms.Form):
    is_delete = forms.IntegerField()
    pub_id = forms.FloatField()
    authors = forms.CharField(max_length=350)
    journ_name = forms.CharField(max_length=300)
    year = forms.IntegerField()


class CoursesForm(forms.Form):
    c_id = forms.FloatField()
    is_delete = forms.IntegerField()
    c_code = forms.CharField(max_length=350)
    c_name = forms.CharField(max_length=300)

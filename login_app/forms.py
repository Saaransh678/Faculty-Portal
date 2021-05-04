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
    # f_name = forms.CharField()
    # s_name = forms.CharField()
    # dept = forms.CharField()


class ProfileChangeForm(forms.Form):
    # fac_id = forms.IntegerField()
    # background = forms.CharField(max_length=350)
    json = forms.JSONField()
    # def __init__(self, *args, **kwargs):
    #     courses = kwargs.pop('courses')
    #     publications = kwargs.pop('pubs')
    #     super(ProfileChangeForm, self).__init__(*args, **kwargs)
    #     counter = 1
    #     for c in courses:
    #         self.fields['course-' + str(counter)] = forms.CharField()
    #         counter += 1

    #     counter = 1
    #     for pub in publications:
    #         self.fields['publication-' + str(counter)] = forms.JSONField()
    #         counter += 1

import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Faculty(models.Model):
    FacultyID = models.IntegerField(primary_key=True)
    dept = models.CharField(max_length=8)
    leaves_remaining = models.IntegerField()
    permission_level = models.IntegerField()


# class CrossCutting(models.Model):
#     ID = models.CharField(max_length=122)
#     FacultyID = models.CharField(max_length=122)
#     name = models.CharField(max_length=122)
#     Permission_level = models.IntegerField()
#     Designation = models.CharField(max_length=122)


class Previous_Cross_Cutting(models.Model):
    # auto incrementing id field
    FacultyID = models.IntegerField()
    timebegin = models.DateTimeField()
    timeend = models.DateTimeField()
    permission_level = models.IntegerField()


class Active_Leave_Entries(models.Model):
    # auto incrementing id field
    FacultyID = models.IntegerField(unique=True)
    application_date = models.DateTimeField()
    starting_date = models.DateField()
    num_leaves = models.IntegerField()
    curr_status = models.IntegerField()
    # description = models.TextField(default="")


class Decision_Record(models.Model):
    # auto incrementing id field
    # Foreign Key with Active_Leave_Entries/Previous_Request_Record
    EntryID = models.IntegerField()
    timecreated = models.DateTimeField()
    body = models.TextField(default="")
    DecisionMakerID = models.IntegerField()
    is_active = models.BooleanField(default=False)
    verdict = models.IntegerField()  # 0 for reject, 1 for more comments, 2 for accepted


class Previous_Request_Record(models.Model):
    EntryID = models.IntegerField()  # Foreign Key with Active_Leave_Entries
    ApplicantID = models.IntegerField()
    starting_date = models.DateField()
    num_leaves = models.IntegerField()
    was_approved = models.BooleanField()


class db_info(models.Model):
    curr_year = models.IntegerField()
    last_clean_date = models.DateField()

import uuid
from django.db import models

# Create your models here.
class Faculty(models.Model):
    ID=models.CharField(max_length=122)
    name=models.CharField(max_length=122)
    dept=models.CharField(max_length=122)
    leaves_remaining=models.IntegerField()
class CrossCutting(models.Model):
    ID=models.CharField(max_length=122)
    FacultyID=models.CharField(max_length=122)
    name=models.CharField(max_length=122)
    Permission_level=models.IntegerField()
    Designation=models.CharField(max_length=122)
class Previous_Cross_Cutting(models.Model):
    FacultyID=models.CharField(max_length=122)
    Timebegin=models.DateField()
    Timeend=models.DateField()
    Permission=models.IntegerField()
class activeleaveentries(models.Model):
    entryid=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    FacultyID=models.CharField(max_length=122)
    application_date=models.DateField()
    Starting_date=models.DateField()
    No_of_leaves=models.IntegerField()
    current_status=models.IntegerField()
    comment=models.TextField()
class comments(model.Model):
    entryid=models.UUIDField()
    body=models.TextField()
    fromfacultyid=models.CharField(max_length=122)
class www(models.Model):
    entryid=models.UUIDField()
    FacultyID=models.CharField(max_length=122)




from django.contrib import admin
from login_app.models import Faculty, CrossCutting, Previous_Cross_Cutting, activeleaveentries, comments,  www
# Register your models here.

admin.site.register(Faculty)
admin.site.register(CrossCutting)
admin.site.register(Previous_Cross_Cutting)
admin.site.register(activeleaveentries)
admin.site.register(comments)
admin.site.register(www)

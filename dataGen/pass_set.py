from django.contrib.auth.models import User
u = User.objects.get(id='100')
u.set_password('new password')
u.save()

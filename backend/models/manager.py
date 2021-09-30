from django.contrib.auth.models import User
from django.db import models


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    
    # https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#extending-the-existing-user-model
    # more stuff here

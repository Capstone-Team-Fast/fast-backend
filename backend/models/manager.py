from django.contrib.auth.models import User
from django.db import models


class Manager(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    modified_on = models.DateTimeField(auto_now=True, editable=False)
    
    # https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#extending-the-existing-user-model

from django.contrib.auth.models import User
from django.db import models


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#extending-the-existing-user-model
    # more stuff here
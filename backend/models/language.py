from django.db import models
from django.contrib.auth.models import User


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)

    user = models.ManyToManyField(User)

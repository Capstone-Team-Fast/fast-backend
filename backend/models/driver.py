from django.contrib.auth.models import User
from django.db import models

from backend.models.availability import Availability
from backend.models.language import Language

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    capacity = models.PositiveIntegerField(null=False)
    employee_status = models.CharField(max_length=15)
    phone = models.CharField(max_length=15, blank=True)
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE)
    languages = models.ManyToManyField(to=Language)

    # https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#extending-the-existing-user-model
    # more stuff here
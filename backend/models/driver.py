from django.contrib.auth.models import User
from django.db import models
from backend.models.availability import Availability
from backend.models.language import Language


class Driver(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True) # https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#extending-the-existing-user-model
    capacity = models.PositiveIntegerField(null=False)
    employee_status = models.CharField(max_length=15)
    phone = models.CharField(max_length=15, blank=True)
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE)
    languages = models.ManyToManyField(to=Language)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    modified_on = models.DateTimeField(auto_now=True, editable=False)

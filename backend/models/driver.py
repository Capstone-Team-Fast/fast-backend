from django.contrib.auth.models import User
from django.db import models
from backend.models.availability import Availability
from backend.models.language import Language


class Driver(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True) # https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#extending-the-existing-user-model
    first_name = models.CharField(max_length=50, default="Jane")
    last_name = models.CharField(max_length=50, default="Doe")
    capacity = models.PositiveIntegerField(null=False)
    employee_status = models.CharField(max_length=15)
    phone = models.CharField(max_length=15, blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True)
    delivery_limit = models.PositiveIntegerField(null=True, blank=True)
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE)
    languages = models.ManyToManyField(to=Language)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    modified_on = models.DateTimeField(auto_now=True, editable=False)

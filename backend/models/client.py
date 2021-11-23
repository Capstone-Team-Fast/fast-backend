from django.contrib.auth.models import User
from django.db import models
from backend.models.language import Language
from backend.models.location import Location


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True) # https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#extending-the-existing-user-model
    first_name = models.CharField(max_length=50, default="John")
    last_name = models.CharField(max_length=50, default="Doe")
    comments = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=False, default=1)
    location = models.ForeignKey(to=Location, on_delete=models.CASCADE, blank=False)
    phone = models.CharField(max_length=15, blank=True)
    languages = models.ManyToManyField(to=Language, blank=False)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    modified_on = models.DateTimeField(auto_now=True, editable=False)

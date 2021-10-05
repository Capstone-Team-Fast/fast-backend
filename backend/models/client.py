from django.contrib.auth.models import User
from django.db import models
from backend.models.route import Route
from backend.models.language import Language


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE) # https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#extending-the-existing-user-model
    quantity = models.PositiveIntegerField(blank=False, default=1)
    route = models.ManyToManyField(to=Route)
    phone = models.CharField(max_length=15, blank=True)
    languages = models.ManyToManyField(to=Language, blank=False)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    modified_on = models.DateTimeField(auto_now=True, editable=False)

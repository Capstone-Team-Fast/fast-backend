from django.db import models


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=50)
    zipcode = models.PositiveIntegerField()
    is_center = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=18, decimal_places=15, editable=False)
    longitude = models.DecimalField(max_digits=18, decimal_places=15, editable=False)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    modified_on = models.DateTimeField(auto_now=True, editable=False)


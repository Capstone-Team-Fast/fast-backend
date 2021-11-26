from django.db import models
from backend.models.driver import Driver
from backend.models.client import Client


class Route(models.Model):
    id = models.AutoField(primary_key=True)
    assigned_to = models.ForeignKey(Driver, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    total_quantity = models.PositiveIntegerField(editable=False, blank=True)
    total_distance = models.DecimalField(max_digits=19, decimal_places=4, editable=False, blank=True)
    total_duration = models.DecimalField(max_digits=19, decimal_places=4, editable=False, blank=True)
    itinerary = models.ManyToManyField(to=Client)

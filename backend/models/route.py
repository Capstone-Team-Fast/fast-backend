from django.db import models
from backend.models.driver import Driver
from backend.models.client import Client
from backend.models.routeList import RouteList


class Route(models.Model):
    id = models.AutoField(primary_key=True)
    assigned_to = models.ForeignKey(Driver, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    total_quantity = models.PositiveIntegerField(blank=True, null=True)
    total_distance = models.DecimalField(max_digits=40, decimal_places=20, blank=True, null=True)
    total_duration = models.DecimalField(max_digits=40, decimal_places=20, blank=True, null=True)
    itinerary = models.JSONField(null=True)
    route_list = models.ForeignKey(RouteList, related_name='routes', on_delete=models.CASCADE, blank=True, null=True)

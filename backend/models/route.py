from django.db import models
from backend.models.driver import Driver


class Route(models.Model):
    assigned_to = models.ForeignKey(Driver, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    modified_on = models.DateTimeField(auto_now=True, editable=False)
    total_quantity = models.PositiveIntegerField(editable=False)
    total_distance = models.DecimalField(max_digits=19, decimal_places=4, editable=False)
    total_duration = models.DecimalField(max_digits=19, decimal_places=4, editable=False)

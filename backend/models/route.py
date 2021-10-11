from django.db import models
from backend.models.driver import Driver


class Route(models.Model):
    id = models.AutoField(primary_key=True)
    assigned_to = models.ForeignKey(Driver, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    total_quantity = models.PositiveIntegerField(editable=False)
    total_distance = models.DecimalField(max_digits=19, decimal_places=4, editable=False)
    total_duration = models.DecimalField(max_digits=19, decimal_places=4, editable=False)

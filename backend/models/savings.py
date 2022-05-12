from django.db import models
from backend.models.location import Location

class Savings(models.Model):
    saving_id = models.AutoField(primary_key=True)
    origin = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="+")
    location1 = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="loc1")
    location2 = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="loc2")
    saving = models.PositiveIntegerField(blank=True, null=True)
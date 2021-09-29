from django.db import models
# from backend.models import driver as DriverModel


class Availability(models.Model):
    sunday = models.BooleanField()
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()
    saturday = models.BooleanField()

    driver = models.ForeignKey('Driver', on_delete=models.CASCADE)

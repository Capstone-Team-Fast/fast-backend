from django.db import models


class RouteList(models.Model):
    id = models.AutoField(primary_key=True)
    solver_status = models.IntegerField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

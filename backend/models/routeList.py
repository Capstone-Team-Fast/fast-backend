from django.db import models
from django.contrib.postgres.fields import ArrayField


class RouteList(models.Model):
    id = models.AutoField(primary_key=True)
    solver_status = models.IntegerField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    others = ArrayField(
        models.IntegerField(blank=True, null=True),
        blank=True, null=True
    )

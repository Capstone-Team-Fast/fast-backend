from django.db import models


class TestModel(models.Model):
    name = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        app_label = "backend"

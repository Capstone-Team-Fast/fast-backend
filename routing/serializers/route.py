from abc import ABC

from rest_framework import serializers


class RouteSerializer(serializers.Serializer, ABC):
    id = serializers.IntegerField()
    total_quantity = serializers.IntegerField()
    total_distance = serializers.IntegerField()
    total_duration = serializers.FloatField()
    created_on = serializers.DateTimeField()
    assigned_to = serializers.CharField()



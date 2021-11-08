from rest_framework import serializers
from backend.models import Route


class RouteSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return Route.objects.create(**validated_data)

    class Meta:
        model = Route
        fields = '__all__'

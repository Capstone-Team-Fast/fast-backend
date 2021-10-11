from rest_framework import serializers

from backend.models import Route


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'
        read_only_fields = ['id', 'created_on']

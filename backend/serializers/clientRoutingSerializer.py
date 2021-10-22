from rest_framework import serializers
from backend.models import Client


class ClientRoutingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id']
        read_only_fields = ['user', 'quantity', 'phone', 'languages', 'location', 'created_on']

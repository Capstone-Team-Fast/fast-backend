from rest_framework import serializers
from backend.models import Client


class ClientRoutingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
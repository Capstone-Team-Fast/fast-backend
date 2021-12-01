from rest_framework import serializers
from backend.models import Client
from backend.serializers import LanguageSerializer, LocationSerializer


class ItinerarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ['id', 'user', 'first_name', 'last_name', 'comments', 'quantity', 'phone']

    def create(self, validated_data):
        return Client.objects.create(**validated_data)
from rest_framework import serializers
from backend.models import Client
from backend.serializers import LanguageSerializer, LocationSerializer


class ItinerarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['location', 'languages']

    # def create(self, validated_data):
    #     return Client.objects.create(**validated_data)
    #
    # def update(self, validated_data):


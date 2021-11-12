from rest_framework import serializers
from django.utils.datetime_safe import datetime
from backend.models import Client, Language, Location
from backend.serializers import LanguageSerializer, LocationSerializer


class ClientSerializer(serializers.ModelSerializer):
    languages = LanguageSerializer(many=True)
    location = LocationSerializer()

    class Meta:
        model = Client
        fields = ['id', 'user', 'first_name', 'last_name', 'quantity', 'phone', 'languages', 'location']
        read_only_fields = ['created_on']

    def create(self, validated_data):
        languages_data = validated_data.pop('languages')
        location_data = validated_data.pop('location')

        if location_data:
            location = Location.objects.create(**location_data)
            client = Client.objects.create(location=location, **validated_data)
        else:
            client = Client.objects.create(**validated_data)

        for language_data in languages_data:
            language, created = Language.objects.get_or_create(name=language_data['name'])
            if not created:
                client.languages.add(language)

        return client

    def update(self, instance, validated_data):
        languages_data = validated_data.pop('languages', [])
        location_data = validated_data.pop('location')
        location = instance.location

        instance.user = validated_data.get('user', instance.user)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.languages.clear()
        instance.modified_on = datetime.now()
        instance.save()

        location.geographic_location = location_data.get('address', location.geographic_location)
        location.city = location_data.get('city', location.city)
        location.state = location_data.get('state', location.state)
        location.zipcode = location_data.get('zipcode', location.zipcode)
        location.is_center = location_data.get('is_center', location.is_center)

        if location_data.get('room_number'):
            location.room_number = location_data.get('room_number', location.room_number)

        if location_data.get('latitude'):
            location.latitude = location_data.get('latitude', location.latitude)

        if location_data.get('longitude'):
            location.longitude = location_data.get('longitude', location.longitude)

        for language_data in languages_data:
            language, created = Language.objects.get_or_create(name=language_data['name'])
            if not created:
                instance.languages.add(language)

        return instance

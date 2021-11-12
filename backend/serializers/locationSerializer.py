from django.utils.datetime_safe import datetime
from rest_framework import serializers
from backend.models.location import Location

# LocationSerializer is very explicit in its serialization
# This can technically be done easier using the ModelSerializer class
# https://www.django-rest-framework.org/api-guide/serializers/#modelserializer


class LocationSerializer(serializers.ModelSerializer):

    address = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=250)
    state = serializers.CharField(max_length=50)
    zipcode = serializers.IntegerField()
    room_number = serializers.CharField(max_length=50, required=False)
    is_center = serializers.BooleanField(default=False)
    latitude = serializers.DecimalField(max_digits=18, decimal_places=15, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=18, decimal_places=15, required=False, allow_null=True)
    # created_on = serializers.DateTimeField()
    # modified_on = serializers.DateTimeField()

    def create(self, validated_data):
        return Location.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.geographic_location = validated_data.get('address', instance.geographic_location)
        instance.city = validated_data.get('city', instance.city)
        instance.state = validated_data.get('state', instance.state)
        instance.zipcode = validated_data.get('zipcode', instance.zipcode)
        instance.is_center = validated_data.get('is_center', instance.is_center)
        instance.room_number = validated_data.get('room_number', instance.room_number)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.modified_on = datetime.now()
        instance.save()
        return instance

    class Meta:
        model = Location
        fields = ['id', 'address', 'city', 'state', 'zipcode', 'is_center', 'room_number', 'latitude',
                  'longitude']
        read_only_fields = ['created_on']

from django.utils.datetime_safe import datetime
from rest_framework import serializers
from backend.models import Driver, Language, Availability
from backend.serializers import AvailabilitySerializer, LanguageSerializer


class DriverSerializer(serializers.ModelSerializer):
    availability = AvailabilitySerializer()
    languages = LanguageSerializer(many=True)
    capacity = serializers.IntegerField(allow_null=False)
    employee_status = serializers.CharField(max_length=15)
    phone = serializers.CharField(max_length=15, allow_null=True)
    duration = serializers.IntegerField(allow_null=True, required=False)
    delivery_limit = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        model = Driver
        fields = ['id', 'user', 'first_name', 'last_name', 'capacity', 'employee_status', 'phone',
                  'duration', 'delivery_limit', 'availability', 'languages']
        read_only_fields = ['created_on']

    def create(self, validated_data):
        availability_data = validated_data.pop('availability')
        languages_data = validated_data.pop('languages')

        if availability_data:
            availability = Availability.objects.create(**availability_data)
            driver = Driver.objects.create(availability=availability, **validated_data)
        else:
            driver = Driver.objects.create(**validated_data)

        for language_data in languages_data:
            language, created = Language.objects.get_or_create(name=language_data['name'])
            if not created:
                driver.languages.add(language)

        return driver

    # TODO: Fix update nested relations
    # https://www.django-rest-framework.org/api-guide/serializers/#writing-update-methods-for-nested-representations
    def update(self, instance, validated_data):
        availability_data = validated_data.pop('availability')
        languages_data = validated_data.pop('languages', [])
        availability = instance.availability

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.capacity = validated_data.get('capacity', instance.capacity)
        instance.employee_status = validated_data.get('employee_status', instance.employee_status)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.delivery_limit = validated_data.get('delivery_limit', instance.delivery_limit)
        instance.modified_on = datetime.now()
        instance.languages.clear()
        instance.save()

        availability.sunday = availability_data.get('sunday', availability.sunday)
        availability.monday = availability_data.get('monday', availability.monday)
        availability.tuesday = availability_data.get('tuesday', availability.tuesday)
        availability.wednesday = availability_data.get('wednesday', availability.wednesday)
        availability.thursday = availability_data.get('thursday', availability.thursday)
        availability.friday = availability_data.get('friday', availability.friday)
        availability.saturday = availability_data.get('saturday', availability.saturday)

        availability.save()

        for language_data in languages_data:
            language, created = Language.objects.get_or_create(name=language_data['name'])
            if not created:
                instance.languages.add(language)

        return instance

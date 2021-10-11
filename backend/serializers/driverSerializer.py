from django.utils.datetime_safe import datetime
from rest_framework import serializers
from backend.models.driver import Driver 

class DriverSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Driver 
        fields = ['user', 'capacity', 'employee_status', 'phone',
                    'availability', 'languages', 'created_on', 'modified_on']
        read_only_fields = ['created_on']
    

    def create(self, validated_data):
        return Driver.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.user = validated_data.get('user', instance.user)
        instance.capacity = validated_data.get('capacity', instance.capacity)
        instance.employee_status = validated_data.get('employee_status', instance.employee_status)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.availability = validated_data.get('availability', instance.availability)
        instance.languages = validated_data.get('languages', instance.languages)
        instance.modified_on = datetime.now()
        instance.save()
        return instance

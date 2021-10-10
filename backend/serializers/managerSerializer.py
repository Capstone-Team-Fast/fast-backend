from django.utils.datetime_safe import datetime
from rest_framework import serializers
from backend.models.manager import Manager

class ManagerSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Manager 
        fields = ['user', 'phone', 'created_on', 'modified_on']
        read_only_fields = ['created_on']
    
    def create(self, validated_data):
        return Manager.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.user = validated_data.get('user', instance.user)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.modified_on = datetime.now()
        instance.save()
        return instance

    

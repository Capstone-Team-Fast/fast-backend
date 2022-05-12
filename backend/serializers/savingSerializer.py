from rest_framework import serializers
from backend.models.savings import Savings
from backend.serializers.locationSerializer import LocationSerializer

class SavingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Savings
        fields = ['saving_id', 'origin', 'location1', 'location2', 'saving']

    # saving_id = serializers.IntegerField()
    # origin = LocationSerializer()
    # location1 = LocationSerializer()
    # location2 = LocationSerializer()
    # saving = serializers.IntegerField()

    # def create(self, validated_data):
    #     return Savings.objects.create(**validated_data)

    # def update(self, instance, validated_data):
    #     instance.saving_id = validated_data.get('saving_id', instance.savings_id)
    #     instance.origin = validated_data.get('origin', instance.origin)
    #     instance.location1 = validated_data.get('location1', instance.location1)
    #     instance.location2 = validated_data.get('location2', instance.location2)      
    #     instance.saving = validated_data.get('saving', instance.savings)
        
    #     instance.save()
    #     return instance

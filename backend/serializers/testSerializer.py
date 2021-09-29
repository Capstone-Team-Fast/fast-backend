from rest_framework import serializers
from backend.models.testModel import TestModel


class TestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, allow_blank=True, default='')

    def create(self, validated_data):
        return TestModel.objects.create(**validated_data)

    def update(self, instance, validated_data):
        return instance

    class Meta:
        model = TestModel
        fields = ['name']

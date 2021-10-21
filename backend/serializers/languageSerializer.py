from rest_framework import serializers

from backend.models import Language


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name']
        read_only_fields = ['created_on']

    # def create(self, validated_data):
    #     queryset = Language.objects.all()
    #
    #
    #     return Language.objects.create(**validated_data)

from rest_framework import serializers
from backend.models import Route, Driver, Client
from backend.serializers import DriverSerializer, ClientSerializer


class RouteSerializer(serializers.ModelSerializer):
    assigned_to = DriverSerializer
    itinerary = ClientSerializer(many=True)

    def create(self, validated_data):
        assigned_to_data = validated_data.pop('assigned_to')
        itinerary_data = validated_data.pop('itinerary')

        assigned_to = Driver.objects.get_or_create(**assigned_to_data)

        route = Route.objects.create(**validated_data)

        for i_data in itinerary_data:
            if i_data.get('is_center') == False or i_data.get('is_center') == 'false':
                i_id = i_data.get('id')
                itinerary = Client.objects.get(id=i_id)
                route.itinerary.add(itinerary)

        return route

    class Meta:
        model = Route
        fields = '__all__'

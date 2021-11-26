from rest_framework import serializers
from backend.models import Route, Driver, Client
from backend.serializers import DriverSerializer, ClientSerializer


class RouteSerializer(serializers.ModelSerializer):
    assigned_to = DriverSerializer
    itinerary = ClientSerializer(many=True)

    def create(self, validated_data):
        assigned_to_data = validated_data.pop('assigned_to')
        itinerary_data = validated_data.pop('itinerary')

        f = open('routing_log', 'a')
        f.write('Assigned_To Data:\n')
        f.write(assigned_to_data)
        f.write('\n')
        f.write('itinerary_data:\n')
        f.write(itinerary_data)
        f.close()

        assigned_to = Driver.objects.get_or_create(**assigned_to_data)

        for i_data in itinerary_data:
            itinerary = Client.objects.get_or_create(**i_data)

        return Route.objects.create(**validated_data)

    class Meta:
        model = Route
        fields = '__all__'

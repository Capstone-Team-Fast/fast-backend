from rest_framework import serializers
from rest_framework.fields import SerializerMethodField, DictField
from backend.models import Route, Driver, Client
from backend.serializers import DriverSerializer, ItinerarySerializer


class RouteSerializer(serializers.ModelSerializer):
    # itinerary = ItinerarySerializer(many=True)
    # assigned_to = DictField(allow_null=True)

    def create(self, validated_data):
        # assigned_to_data = validated_data.pop('assigned_to')
        # itinerary_data = validated_data.pop('itinerary')


        f = open("anger.txt", "a")
        f.write(validated_data)
        f.close()

        route = Route.objects.create(**validated_data)

        # for i_data in itinerary_data:
        #     i_id = i_data.get('id')
        #     itinerary_obj = Client.objects.get(id=i_id)
        #
        #     route.itinerary.add(itinerary_obj)

        # route.itinerary.set(i_list)
        route.save()

        return route

    class Meta:
        model = Route
        fields = ['id', 'assigned_to', 'created_on', 'total_quantity', 'total_distance',
                  'total_duration', 'route_list', 'itinerary']

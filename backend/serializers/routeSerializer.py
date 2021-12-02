from rest_framework import serializers
from rest_framework.fields import SerializerMethodField, DictField
from backend.models import Route, Driver, Client
from backend.serializers import DriverSerializer, ItinerarySerializer


class RouteSerializer(serializers.ModelSerializer):
    itinerary = ItinerarySerializer(many=True)
    assigned_to = DictField()

    def create(self, validated_data):
        assigned_to_data = validated_data.pop('assigned_to')
        itinerary_data = validated_data.pop('itinerary')

        emp_id = assigned_to_data.get('id')

        driver = Driver.objects.get_or_create(id=emp_id)
        # driver_serializer = DriverSerializer(data=driver)
        # driver_instance = None
        #
        # driver_instance = driver_serializer.instance(data=driver)

        # driver_instance = DriverSerializer(data=driver).instance

        # assigned_to = driver.id
        # validated_data.pop('assigned_to')

        route = Route.objects.create(assigned_to=driver, **validated_data)

        # route = Route.objects.create(**validated_data)

        # route.assigned_to.add(assigned_to)

        for i_data in itinerary_data:
            if i_data.get('is_center') == False or i_data.get('is_center') == 'false':
                i_id = i_data.get('id')
                itinerary = Client.objects.get(id=i_id)
                route.itinerary.add(itinerary)

        return route

    class Meta:
        model = Route
        fields = '__all__'

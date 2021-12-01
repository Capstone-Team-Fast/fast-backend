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

        # f = open('driver_log.txt', 'a')
        # f.write('\nAssigned_to Data - \n')
        # f.write(emp_id)
        # f.write('\n')
        # f.close()

        driver = Driver.objects.get_or_create(id=emp_id)
        driver = DriverSerializer(driver)
        assigned_to = driver.save()
        #
        # assigned_to = driver.id

        route = Route.objects.create(assigned_to=assigned_to, **validated_data)

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

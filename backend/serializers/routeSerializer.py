from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from backend.models import Route, Driver, Client
from backend.serializers import DriverSerializer, ItinerarySerializer


class RouteSerializer(serializers.ModelSerializer):
    assigned_to = SerializerMethodField()
    itinerary = ItinerarySerializer(many=True)

    def get_assigned_to(self, obj):
        driver_id = obj.assigned_to.id
        f = open('Route-driver_log.txt', 'a')
        f.write('Object = ')
        f.write(obj)
        f.write('\nAssigned_to Data - \n')
        f.write(driver_id)
        f.write('\n')
        f.close()
        return driver_id

    def create(self, validated_data):
        assigned_to_data = validated_data.get('assigned_to')
        itinerary_data = validated_data.pop('itinerary')

        # emp_id = assigned_to_data.get('id')
        # print('employee id: ' + emp_id + '\n')
        # print(assigned_to_data)
        #


        # driver = Driver.objects.get_or_create(id=emp_id)
        #
        # assigned_to = driver.id

        route = Route.objects.create(assigned_to=assigned_to_data, **validated_data)

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

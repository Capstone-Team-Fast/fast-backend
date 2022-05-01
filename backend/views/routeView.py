from datetime import datetime
import json

from django.http import Http404
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import Route, Client, Driver
from backend.serializers import ClientSerializer, DriverSerializer, RouteListSerializer, RouteSerializer
from routing.managers import RouteManager
from django.conf import settings


class RouteView(APIView):

    def get_object(self, pk):
        try:
            return Route.objects.get(pk=pk)
        except Route.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        route = self.get_object(pk)
        serializer = RouteSerializer(route)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        route = self.get_object(pk)
        route.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RoutingView(APIView):

    def get(self, request, format=None):
        routes = Route.objects.all()
        serializer = RouteSerializer(routes, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        client_id_list = data.get('client_ids')
        driver_id_list = data.get('driver_ids')
        delivery_limit = data.get('delivery_limit')
        departure = data.get('departure')
        duration_limit = data.get('duration_limit')

        departure = json.dumps(departure)

        clients = []
        drivers = []

        for client_id in client_id_list:
            client = Client.objects.get(id=client_id)
            client_serializer = ClientSerializer(client)
            client = JSONRenderer().render(client_serializer.data)
            clients.append(client)

        # client_serializer = ClientSerializer(clients, many=True)

        for driver_id in driver_id_list:
            driver = Driver.objects.get(id=driver_id)
            driver.duration = duration_limit
            if driver.employee_status != 'Employee':
                driver.delivery_limit = delivery_limit
            else:
                driver.deliver_limit = None
            driver.save()
            driver_serializer = DriverSerializer(driver)
            driver = JSONRenderer().render(driver_serializer.data)
            drivers.append(driver)

        # driver_serializer = DriverSerializer(drivers, many=True)

        route_manager = RouteManager(settings.NEOMODEL_NEO4J_BOLT_URL)
        routes_json = route_manager.request_routes(departure, clients, drivers)

        routes_json = json.loads(routes_json)

        for route in routes_json.get('routes'):
            route['assigned_to'] = route['assigned_to']['id']
            # route['itinerary'] = [item for item in route['itinerary'] if(item['is_center'] == False or item['is_center'] == 'false')]

        now = datetime.now()
        now = now.strftime("%m/%d/%Y")

        f = open("routesLog.txt", "a")
        f.write('Route - ')
        f.write(now)
        f.write('\n')
        f.write(json.dumps(routes_json))
        f.write('\n\n')
        f.close()

        # TODO: ensure routes are correctly going through serializer
        #print(type(routes_json))
        serializer = RouteListSerializer(data=routes_json)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # return Response(routes_json, status=status.HTTP_200_OK)

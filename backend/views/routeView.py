import json

from django.http import Http404
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import Route, Client, Driver
from backend.serializers.routeSerializer import RouteSerializer
from backend.serializers import ClientSerializer, DriverSerializer, ClientRoutingSerializer
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


class RouteListView(APIView):

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
            if driver.employee_status != 'Employee':
                driver.delivery_limit = delivery_limit
            else:
                driver.deliver_limit = None
            driver.save()
            driver_serializer = DriverSerializer(driver)
            driver = JSONRenderer().render(driver_serializer.data)
            drivers.append(driver)

        # driver_serializer = DriverSerializer(drivers, many=True)

        # TODO: Test routing app function call
        route_manager = RouteManager(settings.NEO4J_BOLT_URL)
        routes = route_manager.request_routes(departure, clients, drivers)
        routes = json.loads(routes)
        routes = routes.get('routes')

        # TODO: ensure routes are correctly going through serializer
        serializer = RouteSerializer(routes, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import Route, Client, Driver
from backend.serializers.routeSerializer import RouteSerializer
from backend.serializers import ClientSerializer, DriverSerializer, ClientRoutingSerializer, LocationSerializer

from routing.managers import RouteManager


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

        clients = []
        drivers = []

        locations = []

        for client_id in client_id_list:
            client = Client.objects.get(id=client_id)
            location = client.location
            # print(client.location)
            clients.append(client)
            locations.append(location)

        location_serializer = LocationSerializer(locations, many=True)

        client_serializer = ClientSerializer(clients, many=True)

        for driver_id in driver_id_list:
            drivers.append(Driver.objects.get(id=driver_id))

        driver_serializer = DriverSerializer(drivers, many=True)

        # TODO: Connect to routing app with function call like:
        routes = RouteManager.request_routes(client_serializer.data, driver_serializer.data)
        routes = routes.get('routes')

        # TODO: run routes through the route serializer and return response
        serializer = RouteSerializer(routes, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # TODO: remove this when above TODOs are done
        # return Response(driver_serializer.data, status=status.HTTP_200_OK)

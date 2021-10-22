from rest_framework import serializers
from backend.models import Route, Client
from backend.serializers import ClientRoutingSerializer


class RouteSerializer(serializers.ModelSerializer):
    # clients = ClientRoutingSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'clients', 'assigned_to', 'total_duration', 'total_distance', 'total_quantity']

    # TODO: Link to routing microservice
    # TODO: Get client nested data working
    def create(self, validated_data):
        clients_data = validated_data.pop('clients')
        route = Route()
        route.assigned_to = validated_data.get('assigned_to')
        route.clients = 1

        route.total_duration = 1
        route.total_distance = 1
        route.total_quantity = 1

        route.save()

        # clients = Client.objects.get(id=clients_data['id'])
        # route.clients.add(clients)

        # for client_data in clients_data:
        #     client_qs = Client.objects.filter(id__exact=client_data['id'])
        #     if client_qs.exists():
        #         client = client_qs.first()
        #         route.clients.add(client)

        return route

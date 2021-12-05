from rest_framework import serializers
from backend.models import RouteList, Route
from backend.serializers.routeSerializer import RouteSerializer


class RouteListSerializer(serializers.ModelSerializer):
    solver_status = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    routes = RouteSerializer(many=True)

    class Meta:
        model = RouteList
        fields = '__all__'

    def validate_solver_status(self, value):
        if not value:
            return 0
        try:
            return int(value)
        except ValueError:
            raise serializers.ValidationError('You must supply an integer')

    def create(self, validated_data):
        routes_data = validated_data.pop('routes')

        route_list = RouteList.objects.create(**validated_data)

        for route_data in routes_data:
            Route.objects.create(route_list=route_list, **route_data)
            # route_list.routes.add(route_data)

        return route_list

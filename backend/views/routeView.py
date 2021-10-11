from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import Route
from backend.serializers.routeSerializer import RouteSerializer


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

    def post(self, request, format=None):
        serializer = RouteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        route = self.get_object(pk)
        route.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RouteListView(APIView):

    def get(self, request, format=None):
        routes = Route.objects.all()
        serializer = RouteSerializer(routes, many=True)
        return Response(serializer.data)

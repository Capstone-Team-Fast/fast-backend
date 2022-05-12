from django.http import Http404
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import RouteList
from backend.serializers import RouteListSerializer


class RouteListView(APIView):

    def get_object(self, pk):
        try:
            return RouteList.objects.get(pk=pk)
        except RouteList.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        route_list = self.get_object(pk)
        serializer = RouteListSerializer(route_list)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        routeList = self.get_object(pk)
        routeList.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RouteListAllView(APIView):

    def get(self, request, format=None):
        route_lists = RouteList.objects.all()
        serializer = RouteListSerializer(route_lists, many=True)
        return Response(serializer.data)

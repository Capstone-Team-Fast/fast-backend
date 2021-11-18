from rest_framework.views import APIView
from rest_framework.response import Response
from backend.serializers.driverSerializer import DriverSerializer
from rest_framework import status


class BulkDriverView(APIView):

    def post(self, request, format=None):
        serializer = DriverSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

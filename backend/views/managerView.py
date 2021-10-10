from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from backend.models.manager import Manager 
from backend.serializers.managerSerializer import ManagerSerializer
from rest_framework import status
from django.http import Http404

class ManagerView(APIView):

    def get_object(self, pk):
        try:
            return Manager.objects.get(pk=pk)
        except Manager.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        manager = self.get_object(pk)
        serializer = ManagerSerializer(manager)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = ManagerSerializer(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        manager = self.get_object(pk)
        serializer = ManagerSerializer(manager, data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        manager = self.get_object(pk)
        manager.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ManagerListView(APIView):

    def get(self, request, format=None):
        managers = Manager.objects.all()
        serializer = ManagerSerializer(managers, many=True)
        return Response(serializer.data)


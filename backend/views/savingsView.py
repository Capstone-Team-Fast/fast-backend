from django.http import Http404
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models.savings import Savings
from backend.serializers.savingSerializer import SavingsSerializer

class SavingsView(APIView):
    def get_object(self, pk):
        try:
            return Savings.objects.get(pk=pk)
        except:
            Savings.DoesNotExist
            raise Http404

    def get(self, request, pk, format=None):
        saving = self.get_object(pk)
        serializer = SavingsSerializer(saving)
        return Response(serializer.data)
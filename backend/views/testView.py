from rest_framework.views import APIView
from rest_framework.response import Response
from backend.models.testModel import TestModel
from backend.serializers.testSerializer import TestSerializer


class TestView(APIView):

    def get(self, request, format=None):
        tests = TestModel.objects.all()
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data)
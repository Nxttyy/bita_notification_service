from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.models import APIKey
from .serializers import APIKeySerializer


class MonitorAPIView(APIView):
    def success_rate():
        pass
    def failure_rate():
        pass
    def request_count_by_endpoint():
        pass
    def request_count_by_client():
        pass

class APIKeyListView(APIView):
    # permission_classes = [IsAdminUser]


    def get(self, request, format=None):
        api_keys = APIKey.objects.all()
        serializer = APIKeySerializer(api_keys, many=True)  # Serialize all APIKeys
        return Response(serializer.data, status=status.HTTP_200_OK)

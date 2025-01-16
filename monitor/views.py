from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.models import APIKey
from .serializers import APIKeySerializer
from .models import RequestLog


class MonitorAPIView(APIView):
    def get(self, request, format=None):
        total_requests = RequestLog.total_request_count()
        success_count = RequestLog.success_count()
        failure_count = RequestLog.failure_count()

        metrics = {
            "total_requests": total_requests,
            "success_count": success_count,
            "success_rate": success_count / total_requests if total_requests else 0,
            "failure_count": failure_count,
            "failure_rate": failure_count / total_requests if total_requests else 0,
            "request_count_by_endpoint": RequestLog.request_count_by_endpoint(),
            "request_count_by_client": RequestLog.request_count_by_client(),
        }
        return Response(metrics, status=status.HTTP_200_OK)



class APIKeyListView(APIView):
    # permission_classes = [IsAdminUser]


    def get(self, request, format=None):
        api_keys = APIKey.objects.all()
        serializer = APIKeySerializer(api_keys, many=True)  # Serialize all APIKeys
        return Response(serializer.data, status=status.HTTP_200_OK)

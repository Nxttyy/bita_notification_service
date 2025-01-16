from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import RequestLog, APIKey
from .serializers import APIKeySerializer

@extend_schema(
    summary="Get Monitoring Metrics",
    description="Returns metrics including total requests, success/failure rates, request counts by endpoint, and client.",
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "total_requests": {"type": "integer", "example": 250},
                    "success_count": {"type": "integer", "example": 200},
                    "success_rate": {"type": "number", "example": 0.8},
                    "failure_count": {"type": "integer", "example": 50},
                    "failure_rate": {"type": "number", "example": 0.2},
                    "request_count_by_endpoint": {
                        "type": "object",
                        "properties": {
                            "email": {"type": "integer", "example": 120},
                            "sms": {"type": "integer", "example": 80},
                            "in-app": {"type": "integer", "example": 50},
                        },
                    },
                    "request_count_by_client": {
                        "type": "object",
                        "additionalProperties": {"type": "integer", "example": 150},
                    },
                },
            }
        ),
        500: OpenApiResponse(description="Internal server error."),
    },
)
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


@extend_schema(
    summary="List API Keys",
    description="Fetches info on API keys.",
    responses={
        200: OpenApiResponse(
            response={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "example": "uPtZ5RaD.sha512$$....."
                        },
                        "name": {
                            "type": "string",
                            "example": "auth-dev"
                        },
                        "prefix": {
                            "type": "string",
                            "example": "uPtZ5RaD"
                        },
                        "created": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2025-01-15T13:39:28.489015Z"
                        },
                        "revoked": {
                            "type": "boolean",
                            "example": "false"
                        }
                    },                },
            }
        ),
        403: OpenApiResponse(description="Permission denied."),
    },
)
class APIKeyListView(APIView):
    # permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        api_keys = APIKey.objects.all()
        serializer = APIKeySerializer(api_keys, many=True)  # Serialize all APIKeys
        return Response(serializer.data, status=status.HTTP_200_OK)

# from rest_framework.response import Response
# from rest_framework import status
# from django.core.mail import send_mail
# from django.conf import settings
# import logging
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.decorators import api_view, renderer_classes
#
# # logger = logging.getLogger(__name__)
#
# @csrf_exempt
# @api_view(('POST',))
# def send_single_email(request):
#     try:
#         send_mail("My subject",
#                   "the message",
#                   settings.EMAIL_HOST_USER,
#                   ["nathnaelyirga@gmail.com"],
#                   fail_silently=False
#                 )
#
#         return Response({"status": "Email sent successfully"}, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({"status": "Failed to send email", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#

from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
# from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.utils import extend_schema, OpenApiResponse

@csrf_exempt
@extend_schema(
    summary="Send an Email to One/Multiple Recipients",
    description="This endpoint sends an email with a dynamic subject, message, and recipients. The recipients can be provided as a comma-separated list.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'subject': {
                    'type': 'string',
                    'description': 'The subject of the email.',
                    'example': 'Password Reset Email'
                },
                'message': {
                    'type': 'string',
                    'description': 'The content/body of the email.',
                    'example': 'Use the attached link to reset your password:\n <Link>'
                },
                'recipients': {
                    'type': 'string',
                    'description': 'A comma-separated list of email addresses.',
                    'example': 'user1@example.com, user2@example.com'
                },
            },
            'required': ['subject', 'message', 'recipients'],
        }
    },
    responses={
        200: OpenApiResponse(
            description="Email sent successfully",
            examples={
                'application/json': {
                    "status": "Email sent successfully"
                }
            }
        ),
        400: OpenApiResponse(
            description="Missing required fields (subject, message, or recipients)",
            examples={
                'application/json': {
                    "status": "Missing required fields",
                    "error": "subject, message, and recipients are required"
                }
            }
        ),
        500: OpenApiResponse(
            description="Failed to send email due to an internal server error",
            examples={
                'application/json': {
                    "status": "Failed to send email",
                    "error": "SMTP server not responding"
                }
            }
        ),
    }
)

@api_view(('POST',))
def send_single_email(request):
    try:
        # Extracting the dynamic data from the request body
        subject = request.data.get('subject')
        message = request.data.get('message')
        recipients = request.data.get('recipients')

        # Validate if all required fields are present
        if not subject or not message or not recipients:
            return Response(
                {"status": "Missing required fields", "error": "subject, message, and recipients are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure recipients is a list (it can be a comma-separated string)
        if isinstance(recipients, str):
            recipients = [email.strip() for email in recipients.split(',')]

        # Send the email
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipients,  # List of recipients
            fail_silently=False
        )

        return Response({"status": "Email sent successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"status": "Failed to send email", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

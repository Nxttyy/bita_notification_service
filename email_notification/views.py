from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import logging

from django.http import HttpResponse
from rest_framework_api_key.models import APIKey
from django.shortcuts import render
from monitor.models import RequestLog
from .utils import data_from_request, build_error_log

logger = logging.getLogger(__name__)

@csrf_exempt
@extend_schema(
    # parameters=[
    #     OpenApiParameter(
    #         name='Authorization',  # The header name
    #         description='API Key authentication, use format: "Api-Key <API_KEY>"',
    #         required=True,
    #         type=str,
    #         location=OpenApiParameter.HEADER,
    #     ),
    # ],
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
    },
 )

@api_view(('POST',))
def send_single_email(request):

    client_name, ip_address = data_from_request(request)

    try:
        subject = request.data.get('subject')
        message = request.data.get('message')
        recipients = request.data.get('recipients')


        if not subject or not message or not recipients:
            RequestLog.objects.create(sender = client_name, 
                                response_status_code=400,
                                send_to = RequestLog.EMAIL)


            return Response(
                {"status": "Missing required fields", "error": "subject, message, and recipients are required"},
                status=status.HTTP_400_BAD_REQUEST
            )


        # Ensure recipients is a list (it can be a comma-separated string)
        if isinstance(recipients, str):
            recipients = [email.strip() for email in recipients.split(',')]

        # Build email
        html_message = render_to_string('email_template.html', {
            'subject': subject,
            'message': message
        })

        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=recipients
        )
        email.content_subtype = 'html'
        
        email.send(fail_silently=False)

        RequestLog.objects.create(sender = client_name, 
                                response_status_code=200,
                                send_to = RequestLog.EMAIL)

        logger.info(f"{client_name}({ip_address}) sent subject: {subject} to {recipients}")
        return Response({"status": "Email sent successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        my_error = build_error_log(e)
        RequestLog.objects.create(sender = client_name, 
                                response_status_code=500,
                                send_to = RequestLog.EMAIL,
                                error_log = my_error)
        logger.error(e)
        return Response({"status": "Failed to send email", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



def home(request):
    return render(request, 'home.html')


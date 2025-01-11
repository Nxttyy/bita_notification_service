from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
# from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)

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
        subject = request.data.get('subject')
        message = request.data.get('message')
        recipients = request.data.get('recipients')

        if not subject or not message or not recipients:
            return Response(
                {"status": "Missing required fields", "error": "subject, message, and recipients are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure recipients is a list (it can be a comma-separated string)
        if isinstance(recipients, str):
            recipients = [email.strip() for email in recipients.split(',')]

         # Render the HTML template
        html_message = render_to_string('email_template.html', {
            'subject': subject,
            'message': message
        })

        # Create the email message
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=recipients
        )
        email.content_subtype = 'html'  # Specify that the email is HTML

        # Send the email
        email.send(fail_silently=False)

        logger.info(f"email subject: {subject}, sent to {recipients}")
        return Response({"status": "Email sent successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"email sending error:\n{e}")
        return Response({"status": "Failed to send email", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

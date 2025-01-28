import os
import requests
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .schemas import SINGLE_SMS_REQUEST_SCHEMA, SINGLE_SMS_RESPONSES, BULK_SMS_REQUEST_SCHEMA, BULK_SMS_RESPONSES
from django.conf import settings  # Import Django settings



# Custom SMS throttle
class SMSRateThrottle(UserRateThrottle):
    scope = 'sms'


@extend_schema(
    request=SINGLE_SMS_REQUEST_SCHEMA,
    responses=SINGLE_SMS_RESPONSES,
    description="Send a single SMS using the GeezSMS API.",
    summary="Send SMS",
    tags=["SMS"],
)
@api_view(['POST'])
@throttle_classes([SMSRateThrottle]) 
def single_sms(request):
    # Pull the API key from settings
    api_key = settings.SMS_API_KEY
    if not api_key:
        return Response(
            {"error": "Third party authorization failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Extract data from the request body
    phone = request.data.get('phone')
    message = request.data.get('message')

    # Validate required fields
    if not all([phone, message]):
        return Response(
            {"error": "Missing required fields (phone, message)"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Prepare the payload for the GeezSMS API
    payload = {
        "phone": phone,
        "msg": message,
        # "shortcode_id": settings.SMS_SHORT_CODE,
    }

    # Prepare headers
    headers = {
        settings.SMS_API_HEADER_FIELD: api_key,
    }

    response_msg = {}

    # Make the POST request to GeezSMS API
    try:
        response = requests.post(settings.SMS_API_URL, json=payload, headers=headers)
        response_msg = response.json()
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response_msg.get('error') in ['true', "True", True, '1']:
            return Response(
                {"error_message": "Failed to send SMS", **response_msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"status": "SMS sent successfully", **response_msg},
            status=status.HTTP_200_OK
        )
    except requests.exceptions.RequestException as e:
        # Handle any errors from the API request
        return Response(
            {"error_message": f"Failed to send SMS: {str(e)}", **response_msg},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    request=BULK_SMS_REQUEST_SCHEMA,
    responses=BULK_SMS_RESPONSES,
    description="Send bulk SMS.",
    summary="Send Bulk SMS",
    tags=["SMS"],
)
@api_view(['POST'])
@throttle_classes([SMSRateThrottle]) 
def bulk_sms(request):
    # Pull the API key from settings
    api_key = settings.SMS_API_KEY
    if not api_key:
        return Response(
            {"error": "Third party authorization failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Extract data from the request body
    contacts = request.data.get('contacts')
    sender_id = request.data.get('sender_id')
    message = request.data.get('msg')
    notify_url = request.data.get('notify_url')

    # Validate required fields
    if not all([contacts, message, notify_url]):
        return Response(
            {"error": "Missing required fields (contacts, msg, notify_url)"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate contacts
    for contact in contacts:
        if not contact.get('phone_number'):
            return Response(
                {"error": "Each contact must have a 'phone_number' field"},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Prepare payload
    payload = {
        "token": api_key,
        "contacts": contacts,
        "sender_id": sender_id,
        "msg": message,
        "notify_url": notify_url,
    }

    response_msg = {}
    try:
        response = requests.post(settings.SMS_BULK_API_URL, json=payload)
        response_msg = response.json()
        response.raise_for_status()  # Raise an exception for HTTP errors

        if response_msg.get('error') in ['true', "True", True, '1']:
            return Response(
                {"error_message": "Failed to send bulk SMS", **response_msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"status": "Bulk SMS sent successfully", **response.json()},
            status=status.HTTP_200_OK
        )
    except requests.exceptions.RequestException as e:
        # Handle any errors from the API request
        return Response(
            {"error_message": f"Failed to send bulk SMS: {str(e)}", **response_msg},
            status=status.HTTP_400_BAD_REQUEST
        )


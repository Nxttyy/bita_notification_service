from django.db import models
from rest_framework_api_key.models import APIKey

class RequestLog(models.Model):
    # Constants for choices
    EMAIL = 'email'
    SMS = 'sms'
    IN_APP = 'in-app'

    SEND_TO_CHOICES = [
        (EMAIL, 'Email'),
        (SMS, 'SMS'),
        (IN_APP, 'In-App'),
    ]

    id = models.AutoField(primary_key=True)  #
    # sender = models.CharField(max_length=255)  
    sender = models.ForeignKey(APIKey, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)  
    response_status_code = models.IntegerField()  
    send_to = models.CharField(
        max_length=10,
        choices=SEND_TO_CHOICES,
        default=EMAIL,  
    )  

    error_log = models.OneToOneField(
        'ErrorLog',
        on_delete=models.SET_NULL,  
        null=True,                
        blank=True,                 
        related_name='request_log'  
    )

    def __str__(self):
        return f"Request {self.id} from {self.sender} to {self.get_send_to_display()} at {self.sent_at}"

class ErrorLog(models.Model):
    id = models.AutoField(primary_key=True)           
    timestamp = models.DateTimeField(auto_now_add=True) 
    error_type = models.CharField(max_length=255)   
    error_message = models.TextField()                  
    traceback = models.TextField(blank=True, null=True) 

    def __str__(self):
        return f"{self.error_type} at {self.timestamp}"

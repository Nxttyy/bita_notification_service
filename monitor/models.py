from django.db import models

class Request(models.Model):
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
    sender = models.CharField(max_length=255)  
    sent_at = models.DateTimeField(auto_now_add=True)  
    response_status_code = models.IntegerField()  
    send_to = models.CharField(
        max_length=10,
        choices=SEND_TO_CHOICES,
        default=EMAIL,  
    )  

    def __str__(self):
        return f"Request {self.id} from {self.sender} to {self.get_send_to_display()} at {self.sent_at}"

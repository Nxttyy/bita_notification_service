from django.urls import path
from . import views

urlpatterns = [
    # path('send-email/', SendEmailView.as_view(), name='send_email'),
    path('send-single-email/', views.send_single_email, name='send_single_email'),
]

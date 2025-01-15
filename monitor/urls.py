from django.urls import path
from .views import APIKeyListView

urlpatterns = [
    path('api-keys/', APIKeyListView.as_view(), name='api-key-list'),
]

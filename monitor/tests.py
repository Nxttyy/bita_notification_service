from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_api_key.models import APIKey
from rest_framework import status

class APIKeyListViewTest(TestCase):
    def setUp(self):
        # Set up test data
        self.client = APIClient()
        self.api_key1, self.key1 = APIKey.objects.create_key(name="Test Key 1")
        self.api_key2, self.key2 = APIKey.objects.create_key(name="Test Key 2")

    def test_api_key_list_view(self):
        # Perform GET request
        response = self.client.get(reverse('api-key-list'))  # Replace with the actual endpoint

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the data returned
        response_data = response.json()
        self.assertEqual(len(response_data), 2)  # Two API keys created
        self.assertEqual(response_data[0]['name'], "Test Key 1")
        self.assertEqual(response_data[1]['name'], "Test Key 2")
        self.assertIn('id', response_data[0])  # Check if 'id' field is present
        self.assertIn('name', response_data[0])  # Check if 'name' field is present


from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_api_key.models import APIKey
from rest_framework import status

class APIKeyListViewTest(TestCase):
    def setUp(self):
        # Set up test data
        self.client = APIClient()
        
        # Create an API key for authentication
        self.api_key, self.key = APIKey.objects.create_key(name="Test Admin Key")
        
        # Create some test API keys
        self.api_key1, self.key1 = APIKey.objects.create_key(name="Test Key 1")
        self.api_key2, self.key2 = APIKey.objects.create_key(name="Test Key 2")

    def test_api_key_list_view_with_valid_api_key(self):
        # Include the API key in the headers
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {self.key}')
        
        # Perform GET request
        response = self.client.get(reverse('api-key-list'))  # Replace with the actual endpoint
        
        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the data returned
        response_data = response.json()
        self.assertEqual(len(response_data), 3)  # Three (including one for authentication) API keys created
        self.assertEqual(response_data[2]['name'], "Test Admin Key")
        self.assertEqual(response_data[1]['name'], "Test Key 1")
        self.assertEqual(response_data[0]['name'], "Test Key 2")
        self.assertIn('id', response_data[0])  # Check if 'id' field is present
        self.assertIn('name', response_data[0])  # Check if 'name' field is present

    def test_api_key_list_view_with_invalid_api_key(self):
        # Include an invalid API key in the headers
        self.client.credentials(HTTP_AUTHORIZATION='Api-Key invalid-key')
        
        # Perform GET request
        response = self.client.get(reverse('api-key-list'))  # Replace with the actual endpoint
        
        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

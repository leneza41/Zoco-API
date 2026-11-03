from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User


class AccountsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        payload = {
            "username": "nuevo_usuario",
            "email": "nuevo@zoco.com",
            "password": "segurapassword123",
            "role": "SELLER",
            "phone": "4451239999",
            "address": "Calle Morelos #20"
        }
        response = self.client.post('/api/v1/auth/register/', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], "nuevo_usuario")
        self.assertEqual(response.data['user']['role'], "SELLER")

    def test_login_user(self):
        user = User.objects.create_user(
            username="usuario_login",
            password="password123",
            email="login@zoco.com"
        )
        payload = {
            "username": "usuario_login",
            "password": "password123"
        }
        response = self.client.post('/api/v1/auth/login/', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], "usuario_login")

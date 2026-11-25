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

    def test_get_default_user_profile(self):
        response = self.client.get('/api/v1/profile')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['name'], "Comunidad Zoco")
        self.assertEqual(response.data['role'], "Consumidor y Productor Local")
        self.assertIsNone(response.data['photoUrl'])

    def test_update_user_profile_with_local_uri(self):
        payload = {
            "name": "Roberto Gordillo",
            "role": "Consumidor y Productor Local",
            "photoUrl": "file:///data/user/0/com.example.zoco/cache/profile_avatar.jpg"
        }
        response = self.client.put('/api/v1/profile', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['name'], "Roberto Gordillo")
        self.assertEqual(
            response.data['photoUrl'],
            "file:///data/user/0/com.example.zoco/cache/profile_avatar.jpg"
        )

        get_response = self.client.get('/api/v1/profile/')
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['name'], "Roberto Gordillo")

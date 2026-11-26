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
            "phone": "4451239999",
            "address": "Calle Morelos #20"
        }
        response = self.client.post('/api/v1/auth/register/', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], "nuevo_usuario")
        self.assertEqual(response.data['user']['role'], "BUYER")

    def test_register_seller_role_rejected(self):
        payload = {
            "username": "quiere_vender",
            "email": "v@zoco.com",
            "password": "segurapassword123",
            "role": "SELLER",
        }
        response = self.client.post('/api/v1/auth/register', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="quiere_vender").exists())

    def test_register_admin_role_rejected(self):
        payload = {
            "username": "hack_admin",
            "email": "hack@zoco.com",
            "password": "segurapassword123",
            "role": "ADMIN",
        }
        response = self.client.post('/api/v1/auth/register', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data)

    def test_login_user(self):
        User.objects.create_user(
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

    def test_login_never_creates_default_or_admin_accounts(self):
        response = self.client.post(
            '/api/v1/auth/login',
            data={"username": "admin", "password": "admin123"},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='admin').exists())

    def test_superuser_is_always_admin_role(self):
        su = User.objects.create_superuser(username="root", password="password123", email="r@z.com")
        self.assertEqual(su.role, "ADMIN")
        response = self.client.post(
            '/api/v1/auth/login', data={"username": "root", "password": "password123"}, format='json'
        )
        self.assertEqual(response.data['user']['role'], "ADMIN")

    def test_admin_cannot_become_seller(self):
        admin = User.objects.create_user(username="adm", password="password123", role="ADMIN", is_staff=True)
        self.client.force_authenticate(user=admin)
        response = self.client.post('/api/v1/auth/become-seller/', data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        admin.refresh_from_db()
        self.assertEqual(admin.role, "ADMIN")

    def test_profile_singleton_requires_login_and_admin_for_writes(self):
        self.assertEqual(self.client.get('/api/v1/profile').status_code, status.HTTP_401_UNAUTHORIZED)
        buyer = User.objects.create_user(username="b1", password="password123", role="BUYER")
        self.client.force_authenticate(user=buyer)
        self.assertEqual(self.client.get('/api/v1/profile').status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.put('/api/v1/profile', data={"name": "X"}, format='json').status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_become_seller_upgrades_buyer_and_allows_creating_product(self):
        buyer = User.objects.create_user(
            username="buyer_upgrade",
            password="password123",
            role="BUYER",
        )
        self.client.force_authenticate(user=buyer)

        res = self.client.post(
            '/api/v1/auth/become-seller/',
            data={"producerName": "Huerto Nuevo"},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['user']['role'], "SELLER")
        buyer.refresh_from_db()
        self.assertEqual(buyer.role, "SELLER")
        self.assertEqual(buyer.first_name, "Huerto Nuevo")

        product_res = self.client.post(
            '/api/v1/products',
            data={
                "name": "Mermelada Casera",
                "price": 65.0,
                "producerName": "Huerto Nuevo",
                "category": "BAKERY",
            },
            format='json',
        )
        self.assertEqual(product_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(product_res.data['sellerId'], buyer.id)
        self.assertEqual(product_res.data['sellerUsername'], buyer.username)

    def test_admin_can_change_user_role_and_non_admin_forbidden(self):
        admin = User.objects.create_user(
            username="admin_test",
            password="password123",
            role="ADMIN",
            is_staff=True,
        )
        target = User.objects.create_user(
            username="target_user",
            password="password123",
            role="BUYER",
        )

        # Non-admin cannot access user role endpoint
        self.client.force_authenticate(user=target)
        forbidden_res = self.client.post(
            f'/api/v1/users/{target.id}/role',
            data={"role": "ADMIN"},
            format='json',
        )
        self.assertEqual(forbidden_res.status_code, status.HTTP_403_FORBIDDEN)

        # Admin can change role
        self.client.force_authenticate(user=admin)
        ok_res = self.client.post(
            f'/api/v1/users/{target.id}/role/',
            data={"role": "SELLER"},
            format='json',
        )
        self.assertEqual(ok_res.status_code, status.HTTP_200_OK)
        self.assertEqual(ok_res.data['role'], "SELLER")
        target.refresh_from_db()
        self.assertEqual(target.role, "SELLER")

    def _login_admin(self):
        admin = User.objects.create_user(username="adm_p", password="password123", role="ADMIN", is_staff=True)
        self.client.force_authenticate(user=admin)

    def test_get_default_user_profile(self):
        self._login_admin()
        response = self.client.get('/api/v1/profile')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['name'], "Comunidad Zoco")
        self.assertEqual(response.data['role'], "Consumidor y Productor Local")
        self.assertIsNone(response.data['photoUrl'])

    def test_update_user_profile_with_local_uri(self):
        self._login_admin()
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

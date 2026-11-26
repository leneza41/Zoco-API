from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from notifications.models import Notification, NotificationType


class NotificationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(username="dueno", password="password123", role="BUYER")
        self.other = User.objects.create_user(username="otro", password="password123", role="BUYER")
        self.notif = Notification.objects.create(
            title="Nuevo pedido recibido",
            message="Tienes un nuevo pedido pendiente de confirmación",
            type=NotificationType.ORDER_STATUS,
            is_read=False,
            user=self.owner
        )

    def test_notifications_require_login(self):
        self.assertEqual(self.client.get('/api/v1/notifications').status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_see_or_create_others_notifications(self):
        self.client.force_authenticate(user=self.other)
        self.assertEqual(len(self.client.get('/api/v1/notifications').data), 0)
        res = self.client.post('/api/v1/notifications', data={"title": "x", "message": "y"}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_notifications(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get('/api/v1/notifications')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)

    def test_mark_notification_as_read(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/v1/notifications/{self.notif.id}/read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notif.refresh_from_db()
        self.assertTrue(self.notif.is_read)

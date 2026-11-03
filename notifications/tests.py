from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from notifications.models import Notification, NotificationType


class NotificationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.notif = Notification.objects.create(
            title="Nuevo pedido recibido",
            message="Tienes un nuevo pedido pendiente de confirmación",
            type=NotificationType.ORDER_STATUS,
            is_read=False
        )

    def test_list_notifications(self):
        response = self.client.get('/api/v1/notifications')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)

    def test_mark_notification_as_read(self):
        response = self.client.post(f'/api/v1/notifications/{self.notif.id}/read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notif.refresh_from_db()
        self.assertTrue(self.notif.is_read)

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Product, ProductCategory
from orders.models import Order, OrderStatus
from accounts.models import User


class OrderAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='comprador_test',
            password='password123',
            role='BUYER'
        )
        self.product = Product.objects.create(
            name="Café de Altura en Grano",
            description="Tostado artesanal",
            price=150.00,
            category=ProductCategory.PRODUCE,
            producer_name="Finca Los Pinos",
            is_express_delivery=True,
            in_stock=True
        )

    def test_create_order_with_items(self):
        payload = {
            "customerName": "Juan Carlos",
            "customerPhone": "4451112233",
            "deliveryAddress": "Calle Galeana #10",
            "scheduledTime": "17:00 hrs",
            "isExpress": True,
            "items": [
                {
                    "productId": self.product.id,
                    "quantity": 2,
                    "unitPrice": 150.0
                }
            ]
        }
        response = self.client.post('/api/v1/orders', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customerName'], "Juan Carlos")
        self.assertEqual(response.data['totalAmount'], 300.0)
        self.assertEqual(len(response.data['items']), 1)

    def test_change_order_status(self):
        order = Order.objects.create(
            customer_name="María",
            total_amount=150.00,
            status=OrderStatus.PENDING
        )
        response = self.client.post(
            f'/api/v1/orders/{order.id}/status/',
            data={"status": "CONFIRMED"},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.CONFIRMED)

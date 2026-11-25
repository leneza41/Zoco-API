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

    def test_create_order_deducts_stock_and_updates_in_stock(self):
        self.product.stock = 3
        self.product.save()

        # Comprar 2 unidades -> debe quedar 1 y seguir en stock
        payload = {
            "customerName": "Ana",
            "items": [{"productId": self.product.id, "quantity": 2}]
        }
        response = self.client.post('/api/v1/orders', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)
        self.assertTrue(self.product.in_stock)

        # Comprar la última unidad -> debe quedar 0 e in_stock = False
        payload_last = {
            "customerName": "Ana",
            "items": [{"productId": self.product.id, "quantity": 1}]
        }
        response_last = self.client.post('/api/v1/orders', data=payload_last, format='json')
        self.assertEqual(response_last.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 0)
        self.assertFalse(self.product.in_stock)

    def test_create_order_insufficient_stock_rejected(self):
        self.product.stock = 2
        self.product.save()

        payload = {
            "customerName": "Carlos",
            "items": [{"productId": self.product.id, "quantity": 5}]
        }
        response = self.client.post('/api/v1/orders', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)
        self.assertEqual(Order.objects.count(), 0)

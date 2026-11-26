from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Product, ProductCategory
from orders.models import Order, OrderItem, OrderStatus
from accounts.models import User


class OrderAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='comprador_test',
            password='password123',
            role='BUYER'
        )
        self.seller = User.objects.create_user(
            username='vendedor_test',
            password='password123',
            role='SELLER'
        )
        self.other_seller = User.objects.create_user(
            username='otro_vendedor',
            password='password123',
            role='SELLER'
        )
        self.admin = User.objects.create_user(
            username='admin_test',
            password='password123',
            role='ADMIN',
            is_staff=True,
        )
        self.product = Product.objects.create(
            name="Café de Altura en Grano",
            description="Tostado artesanal",
            price=150.00,
            category=ProductCategory.PRODUCE,
            producer_name="Finca Los Pinos",
            seller=self.seller,
            is_express_delivery=True,
            in_stock=True
        )
        self.other_product = Product.objects.create(
            name="Taza de Barro",
            description="Hecha a mano",
            price=80.00,
            category=ProductCategory.CRAFTS,
            producer_name="Taller Sur",
            seller=self.other_seller,
            is_express_delivery=False,
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
        self.assertEqual(response.data['items'][0]['sellerUsername'], self.seller.username)

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

    def test_buyer_cannot_confirm_order_but_can_cancel(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="Comprador Test",
            total_amount=150.00,
            status=OrderStatus.PENDING,
        )
        self.client.force_authenticate(user=self.user)

        forbidden_res = self.client.patch(
            f'/api/v1/orders/{order.id}/status',
            data={"status": "CONFIRMED"},
            format='json',
        )
        self.assertEqual(forbidden_res.status_code, status.HTTP_403_FORBIDDEN)

        cancel_res = self.client.post(
            f'/api/v1/orders/{order.id}/status',
            data={"status": "CANCELLED"},
            format='json',
        )
        self.assertEqual(cancel_res.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.CANCELLED)

    def test_order_queryset_filtered_by_role(self):
        order_for_seller = Order.objects.create(
            user=self.user,
            customer_name="Laura",
            total_amount=150.00,
        )
        OrderItem.objects.create(
            order=order_for_seller,
            product=self.product,
            product_name=self.product.name,
            quantity=1,
            unit_price=150.00,
            subtotal=150.00,
        )
        order_for_other_seller = Order.objects.create(
            user=self.other_seller,
            customer_name="Otro",
            total_amount=80.00,
        )
        OrderItem.objects.create(
            order=order_for_other_seller,
            product=self.other_product,
            product_name=self.other_product.name,
            quantity=1,
            unit_price=80.00,
            subtotal=80.00,
        )

        # Buyer sees only own order
        self.client.force_authenticate(user=self.user)
        buyer_res = self.client.get('/api/v1/orders')
        self.assertEqual(len(buyer_res.data), 1)
        self.assertEqual(buyer_res.data[0]['id'], order_for_seller.id)

        # Seller sees order containing their product
        self.client.force_authenticate(user=self.seller)
        seller_res = self.client.get('/api/v1/orders')
        self.assertEqual(len(seller_res.data), 1)
        self.assertEqual(seller_res.data[0]['id'], order_for_seller.id)

        # Admin sees all orders
        self.client.force_authenticate(user=self.admin)
        admin_res = self.client.get('/api/v1/orders')
        self.assertEqual(len(admin_res.data), 2)

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

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from products.models import Product, ProductCategory


class ProductAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.seller = User.objects.create_user(
            username="vendedor_test",
            password="password123",
            role="SELLER",
        )
        self.other_seller = User.objects.create_user(
            username="otro_vendedor",
            password="password123",
            role="SELLER",
        )
        self.buyer = User.objects.create_user(
            username="comprador_test",
            password="password123",
            role="BUYER",
        )
        self.admin = User.objects.create_user(
            username="admin_test",
            password="password123",
            role="ADMIN",
            is_staff=True,
        )
        self.product1 = Product.objects.create(
            name="Pan de Muerto Tradicional",
            description="Pan elaborado con azahar y mantequilla",
            price=25.00,
            category=ProductCategory.BAKERY,
            producer_name="Panadería La Flor",
            seller=self.seller,
            is_express_delivery=True,
            in_stock=True
        )
        self.product2 = Product.objects.create(
            name="Miel Pura de Abeja",
            description="Miel silvestre de la sierra",
            price=90.00,
            category=ProductCategory.PRODUCE,
            producer_name="Apiario Don Lupe",
            seller=self.other_seller,
            is_express_delivery=False,
            in_stock=True
        )

    def test_list_products_returns_list_format(self):
        """El endpoint debe retornar una lista directa compatible con Android Retrofit List<ProductDto>"""
        response = self.client.get('/api/v1/products')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)

        first = response.data[0]
        # Verificar campos camelCase requeridos por Android Moshi ProductDto
        self.assertIn('id', first)
        self.assertIn('name', first)
        self.assertIn('price', first)
        self.assertIn('producerName', first)
        self.assertIn('sellerId', first)
        self.assertIn('sellerUsername', first)
        self.assertIn('isExpressDelivery', first)
        self.assertIn('inStock', first)
        self.assertIsInstance(first['price'], float)

    def test_list_products_with_trailing_slash(self):
        """Debe responder igual con barra diagonal al final"""
        response = self.client.get('/api/v1/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_filter_by_category(self):
        response = self.client.get('/api/v1/products?category=BAKERY')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Pan de Muerto Tradicional")

    def test_filter_by_express_delivery(self):
        response = self.client.get('/api/v1/products?isExpressDelivery=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['isExpressDelivery'], True)

    def test_search_product(self):
        response = self.client.get('/api/v1/products?search=Miel')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Miel Pura de Abeja")

    def test_get_product_by_id(self):
        response = self.client.get(f'/api/v1/products/{self.product1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.product1.id)
        self.assertEqual(response.data['name'], "Pan de Muerto Tradicional")
        self.assertEqual(response.data['sellerId'], self.seller.id)
        self.assertEqual(response.data['sellerUsername'], self.seller.username)

    def test_create_product_with_camel_case(self):
        """Debe permitir crear productos con payload en camelCase desde Android autenticado como SELLER"""
        self.client.force_authenticate(user=self.seller)
        payload = {
            "name": "Queso Crema Ranchero",
            "description": "Elaborado artesanalmente",
            "price": 50.0,
            "category": "DAIRY",
            "producerName": "Rancho San José",
            "isExpressDelivery": True,
            "inStock": True
        }
        response = self.client.post('/api/v1/products', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], "Queso Crema Ranchero")
        self.assertEqual(response.data['producerName'], "Rancho San José")
        self.assertEqual(response.data['isExpressDelivery'], True)
        self.assertEqual(response.data['sellerId'], self.seller.id)
        self.assertEqual(response.data['sellerUsername'], self.seller.username)

    def test_update_product(self):
        self.client.force_authenticate(user=self.seller)
        payload = {
            "name": "Pan de Muerto Especial",
            "price": 28.0,
            "producerName": "Panadería La Flor",
            "category": "BAKERY"
        }
        response = self.client.put(f'/api/v1/products/{self.product1.id}', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.name, "Pan de Muerto Especial")
        self.assertEqual(float(self.product1.price), 28.0)

    def test_delete_own_product_as_seller(self):
        self.client.force_authenticate(user=self.seller)
        response = self.client.delete(f'/api/v1/products/{self.product1.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product1.id).exists())

    def test_seller_cannot_delete_other_sellers_product(self):
        self.client.force_authenticate(user=self.seller)
        response = self.client.delete(f'/api/v1/products/{self.product2.id}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(id=self.product2.id).exists())

    def test_buyer_cannot_create_or_delete_product(self):
        self.client.force_authenticate(user=self.buyer)
        create_res = self.client.post(
            '/api/v1/products',
            data={
                "name": "Producto Bloqueado",
                "price": 30.0,
                "producerName": "Comprador",
            },
            format='json',
        )
        self.assertEqual(create_res.status_code, status.HTTP_403_FORBIDDEN)

        delete_res = self.client.delete(f'/api/v1/products/{self.product1.id}')
        self.assertEqual(delete_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.filter(id=self.product1.id).exists())

    def test_admin_can_delete_any_product(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/v1/products/{self.product2.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product2.id).exists())

    def test_product_stock_and_image_url(self):
        self.client.force_authenticate(user=self.seller)
        payload = {
            "name": "Pan de Campo Artesanal",
            "description": "Pan rústico de masa madre",
            "price": 45.0,
            "category": "BAKERY",
            "producerName": "Panadería Tradicional",
            "isExpressDelivery": True,
            "stock": 15,
            "imageUrl": "file:///data/user/0/com.example.zoco/cache/pan.jpg"
        }
        response = self.client.post('/api/v1/products', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['stock'], 15)
        self.assertEqual(response.data['inStock'], True)
        self.assertEqual(response.data['imageUrl'], "file:///data/user/0/com.example.zoco/cache/pan.jpg")

    def test_product_stock_zero_sets_in_stock_false(self):
        self.client.force_authenticate(user=self.seller)
        payload = {
            "name": "Producto Agotado",
            "price": 20.0,
            "producerName": "Productor Local",
            "stock": 0,
            "inStock": True
        }
        response = self.client.post('/api/v1/products', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['stock'], 0)
        self.assertEqual(response.data['inStock'], False)

    def test_product_negative_stock_rejected(self):
        self.client.force_authenticate(user=self.seller)
        payload = {
            "name": "Producto Inválido",
            "price": 20.0,
            "producerName": "Productor Local",
            "stock": -5
        }
        response = self.client.post('/api/v1/products', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock', response.data)

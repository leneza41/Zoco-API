from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Product, ProductCategory


class ProductAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product1 = Product.objects.create(
            name="Pan de Muerto Tradicional",
            description="Pan elaborado con azahar y mantequilla",
            price=25.00,
            category=ProductCategory.BAKERY,
            producer_name="Panadería La Flor",
            is_express_delivery=True,
            in_stock=True
        )
        self.product2 = Product.objects.create(
            name="Miel Pura de Abeja",
            description="Miel silvestre de la sierra",
            price=90.00,
            category=ProductCategory.PRODUCE,
            producer_name="Apiario Don Lupe",
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

    def test_create_product_with_camel_case(self):
        """Debe permitir crear productos con payload en camelCase desde Android"""
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

    def test_update_product(self):
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

    def test_delete_product(self):
        response = self.client.delete(f'/api/v1/products/{self.product1.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product1.id).exists())

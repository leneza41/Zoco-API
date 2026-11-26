import io
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from products.models import Product

TEMP_MEDIA = tempfile.mkdtemp()


def make_image(name="foto.png", size=(20, 20)):
    buffer = io.BytesIO()
    Image.new("RGB", size, "red").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class ImageUploadTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.client = APIClient()
        self.seller = User.objects.create_user(username="v1", password="password123", role="SELLER")
        self.other = User.objects.create_user(username="v2", password="password123", role="SELLER")
        self.buyer = User.objects.create_user(username="c1", password="password123", role="BUYER")
        self.admin = User.objects.create_user(username="a1", password="password123", role="ADMIN", is_staff=True)
        self.product = Product.objects.create(name="Pan", price=10, producer_name="Panadería", seller=self.seller)

    def upload(self, user, image=None, product=None):
        self.client.force_authenticate(user=user)
        product = product or self.product
        return self.client.post(
            f'/api/v1/products/{product.id}/image',
            data={"image": image or make_image()},
            format='multipart',
        )

    def test_owner_uploads_product_image_and_gets_absolute_url(self):
        res = self.upload(self.seller)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['imageUrl'].startswith('http://testserver/media/products/'))
        self.product.refresh_from_db()
        self.assertTrue(self.product.image)

        listing = self.client.get('/api/v1/products')
        self.assertTrue(listing.data[0]['imageUrl'].startswith('http://testserver/media/products/'))

    def test_admin_can_upload_for_any_product(self):
        self.assertEqual(self.upload(self.admin).status_code, status.HTTP_200_OK)

    def test_other_seller_and_buyer_cannot_upload(self):
        self.assertEqual(self.upload(self.other).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.upload(self.buyer).status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_upload(self):
        self.client.force_authenticate(user=None)
        res = self.client.post(
            f'/api/v1/products/{self.product.id}/image', data={"image": make_image()}, format='multipart'
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_image_file_rejected(self):
        fake = SimpleUploadedFile("virus.png", b"no soy una imagen", content_type="image/png")
        self.assertEqual(self.upload(self.seller, fake).status_code, status.HTTP_400_BAD_REQUEST)

    def test_local_phone_uri_is_not_stored_as_image_url(self):
        self.client.force_authenticate(user=self.seller)
        res = self.client.post(
            '/api/v1/products',
            data={"name": "Miel", "price": 50, "producerName": "Apiario", "imageUrl": "content://media/external/1"},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(res.data['imageUrl'])

    def test_user_uploads_avatar(self):
        self.client.force_authenticate(user=self.buyer)
        res = self.client.post('/api/v1/auth/me/avatar', data={"image": make_image()}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['user']['avatar'].startswith('http://testserver/media/avatars/'))

    def test_avatar_requires_login(self):
        self.client.force_authenticate(user=None)
        res = self.client.post('/api/v1/auth/me/avatar', data={"image": make_image()}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

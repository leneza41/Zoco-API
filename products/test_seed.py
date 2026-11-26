import shutil
import tempfile

from django.core.management import call_command
from django.test import TestCase, override_settings

from products.models import Product


class SeedDataTests(TestCase):
    """El comando seed_data debe dejar todos los productos con foto y sin textos de desarrollador."""

    def test_seed_creates_products_with_photos(self):
        media_dir = tempfile.mkdtemp()
        try:
            with override_settings(MEDIA_ROOT=media_dir):
                call_command('seed_data', verbosity=0)
                products = list(Product.objects.all())
                self.assertEqual(len(products), 10)
                for product in products:
                    self.assertTrue(product.image, f'{product.name} sin foto')
                    self.assertNotIn('[', product.name)
                    self.assertNotIn('Web API', product.producer_name)
        finally:
            shutil.rmtree(media_dir, ignore_errors=True)

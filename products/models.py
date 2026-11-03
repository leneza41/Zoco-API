from django.db import models
from django.conf import settings


class ProductCategory(models.TextChoices):
    ALL = 'ALL', 'Todas las categorías'
    BAKERY = 'BAKERY', 'Panadería y Repostería'
    PRODUCE = 'PRODUCE', 'Frutas y Verduras'
    DAIRY = 'DAIRY', 'Lácteos y Derivados'
    CRAFTS = 'CRAFTS', 'Artesanías'


class Product(models.Model):
    name = models.CharField(max_length=200, help_text="Nombre del producto")
    description = models.TextField(blank=True, default="", help_text="Descripción detallada del producto")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio en pesos")
    category = models.CharField(
        max_length=50,
        choices=ProductCategory.choices,
        default=ProductCategory.ALL,
        help_text="Categoría del producto (ALL, BAKERY, PRODUCE, DAIRY, CRAFTS)"
    )
    producer_name = models.CharField(max_length=150, help_text="Nombre del productor o artesano local")
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        help_text="Usuario vendedor propietario"
    )
    is_express_delivery = models.BooleanField(
        default=False,
        help_text="Indica si el producto cuenta con entrega express el mismo día"
    )
    in_stock = models.BooleanField(
        default=True,
        help_text="Indica si hay existencias disponibles del producto"
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True, help_text="Fotografía principal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return f"{self.name} - ${self.price} ({self.producer_name})"

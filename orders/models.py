from django.db import models
from django.conf import settings
from products.models import Product


class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pendiente'
    CONFIRMED = 'CONFIRMED', 'Confirmado'
    PREPARING = 'PREPARING', 'En preparación'
    OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY', 'En camino'
    DELIVERED = 'DELIVERED', 'Entregado'
    CANCELLED = 'CANCELLED', 'Cancelado'


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        help_text="Usuario comprador"
    )
    customer_name = models.CharField(max_length=150, blank=True, help_text="Nombre del comprador")
    customer_phone = models.CharField(max_length=30, blank=True, help_text="Teléfono de contacto")
    delivery_address = models.TextField(blank=True, help_text="Dirección de entrega")
    scheduled_time = models.CharField(
        max_length=100,
        blank=True,
        help_text="Horario o franja horaria de entrega programada"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Monto total del pedido"
    )
    status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        help_text="Estado actual del pedido"
    )
    is_express = models.BooleanField(
        default=False,
        help_text="Indica si el pedido tiene solicitud de envío express"
    )
    notes = models.TextField(blank=True, help_text="Instrucciones especiales de entrega")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"Pedido #{self.id} - ${self.total_amount} ({self.get_status_display()})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items'
    )
    product_name = models.CharField(max_length=200, help_text="Nombre del producto al momento de comprar")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedidos'

    def save(self, *args, **kwargs):
        if not self.subtotal:
            self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} (${self.subtotal})"

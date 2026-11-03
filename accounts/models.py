from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('BUYER', 'Comprador'),
        ('SELLER', 'Vendedor'),
        ('ADMIN', 'Administrador'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='BUYER',
        help_text="Rol del usuario en la plataforma Zoco"
    )
    phone = models.CharField(max_length=20, blank=True, help_text="Teléfono de contacto")
    address = models.TextField(blank=True, help_text="Dirección física o de entrega")
    preferred_language = models.CharField(max_length=10, default='es', help_text="Idioma preferido (es, en)")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

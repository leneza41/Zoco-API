from django.db import models
from products.models import Product


class MediaType(models.TextChoices):
    IMAGE = 'IMAGE', 'Imagen'
    VIDEO = 'VIDEO', 'Video'
    DOCUMENT = 'DOCUMENT', 'Documento'


class Media(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='media_items',
        help_text="Producto al que pertenece el recurso (opcional)"
    )
    file = models.FileField(upload_to='media_uploads/', blank=True, null=True, help_text="Archivo subido")
    media_uri = models.CharField(max_length=500, blank=True, help_text="URI o URL externa/local del recurso")
    media_type = models.CharField(
        max_length=20,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
        help_text="Tipo de archivo multimedia"
    )
    description = models.CharField(max_length=255, blank=True, default="", help_text="Descripción o pie de foto")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Multimedia'
        verbose_name_plural = 'Archivos Multimedia'

    def save(self, *args, **kwargs):
        if self.file and not self.media_uri:
            # Set media_uri to file url automatically if empty
            self.media_uri = self.file.url if hasattr(self.file, 'url') else str(self.file)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Media #{self.id} ({self.media_type}) - {self.description or self.media_uri}"

from django.db import models
from django.conf import settings


class NotificationType(models.TextChoices):
    INFO = 'INFO', 'Información'
    ORDER_STATUS = 'ORDER_STATUS', 'Estado de Pedido'
    ALERT = 'ALERT', 'Alerta'
    PROMOTION = 'PROMOTION', 'Promoción'


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        help_text="Usuario destinatario (opcional para notificaciones globales)"
    )
    title = models.CharField(max_length=200, help_text="Título de la notificación")
    message = models.TextField(help_text="Contenido del mensaje")
    is_read = models.BooleanField(default=False, help_text="Indica si la notificación ha sido leída")
    type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
        help_text="Tipo de notificación"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f"{self.title} ({self.type}) - {'Leída' if self.is_read else 'Nueva'}"

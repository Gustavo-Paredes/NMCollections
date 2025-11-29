from django.conf import settings
from django.db import models
from django.utils import timezone
from django.db.models import Q


class SupportThread(models.Model):
    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Abierto'),
        (STATUS_CLOSED, 'Cerrado'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_threads',
        verbose_name='Usuario'
    )
    assigned_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_threads',
        verbose_name='Administrador asignado'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Hilo de Soporte'
        verbose_name_plural = 'Hilos de Soporte'
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=Q(status='open'),
                name='unique_open_thread_per_user'
            )
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f"Soporte de {self.user} ({self.get_status_display()})"


class SupportMessage(models.Model):
    thread = models.ForeignKey(
        SupportThread,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Hilo'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_messages',
        verbose_name='Remitente'
    )
    content = models.TextField('Mensaje')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Mensaje de Soporte'
        verbose_name_plural = 'Mensajes de Soporte'
        ordering = ['id']
        indexes = [
            models.Index(fields=['thread', 'id']),
            models.Index(fields=['thread', 'created_at']),
        ]

    def __str__(self):
        return f"Msg {self.id} en hilo {self.thread_id} por {self.sender_id}"

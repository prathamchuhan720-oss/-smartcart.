"""
Notification model for SmartCart notifications app.
"""
from django.conf import settings
from django.db import models
from core.models import TimeStampedModel


class Notification(TimeStampedModel):
    """
    In-app alerts and notifications for users.
    """
    class NotificationType(models.TextChoices):
        ORDER = 'order', 'Order Update'
        INVENTORY = 'inventory', 'Stock Alert'
        PROMOTION = 'promotion', 'Special Offer'
        SYSTEM = 'system', 'System Notice'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.ORDER,
    )
    is_read = models.BooleanField(default=False, db_index=True)
    link = models.CharField(max_length=255, blank=True, help_text="Relative frontend route e.g. /orders/123")

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.title} for {self.user.email}"

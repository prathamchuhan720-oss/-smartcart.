"""
Base models for SmartCart.

Provides reusable abstract base classes that all app models should inherit from.
"""
import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    ``created_at`` and ``updated_at`` fields.

    All SmartCart models should inherit from this.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class UUIDModel(TimeStampedModel):
    """
    Abstract base model that uses UUID as primary key.

    Use for models where sequential IDs would be a security concern
    (e.g., orders, payments).
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta(TimeStampedModel.Meta):
        abstract = True

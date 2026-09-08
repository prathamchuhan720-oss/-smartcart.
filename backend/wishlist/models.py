"""
Wishlist and WishlistItem models for SmartCart wishlist app.
"""
from django.conf import settings
from django.db import models
from core.models import TimeStampedModel
from products.models import Product


class Wishlist(TimeStampedModel):
    """
    Customer's Wishlist.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist',
    )

    class Meta:
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'

    def __str__(self):
        return f"Wishlist of {self.user.email}"

    @property
    def total_items(self):
        return self.items.count()


class WishlistItem(TimeStampedModel):
    """
    Item stored in a customer's wishlist.
    """
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='wishlist_items',
    )

    class Meta:
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        unique_together = ['wishlist', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} in {self.wishlist}"

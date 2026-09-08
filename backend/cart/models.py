"""
Cart and CartItem models for SmartCart cart app.
"""
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from core.models import TimeStampedModel
from products.models import ProductVariant


class Cart(TimeStampedModel):
    """
    Shopping cart associated with an authenticated User or a guest session.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart',
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.email}"
        return f"Guest Cart ({self.session_key})"

    @property
    def subtotal(self):
        return sum((item.subtotal for item in self.items.all()), Decimal('0.00'))

    @property
    def total_items(self):
        return sum((item.quantity for item in self.items.all()), 0)

    def clear(self):
        self.items.all().delete()


class CartItem(TimeStampedModel):
    """
    Individual line item in a Cart.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='cart_items',
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'variant']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.quantity}x {self.variant} in Cart"

    @property
    def unit_price(self):
        return self.variant.price

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

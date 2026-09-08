"""
Inventory and InventoryHistory models for SmartCart inventory app.
"""
from django.conf import settings
from django.db import models
from core.models import TimeStampedModel
from products.models import ProductVariant


class Inventory(TimeStampedModel):
    """
    Inventory tracking per ProductVariant.
    """
    class StockStatus(models.TextChoices):
        IN_STOCK = 'in_stock', 'In Stock'
        LOW_STOCK = 'low_stock', 'Low Stock'
        OUT_OF_STOCK = 'out_of_stock', 'Out of Stock'

    variant = models.OneToOneField(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='inventory',
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)

    class Meta:
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventories'

    def __str__(self):
        return f"Inventory: {self.variant} (Stock: {self.available_stock})"

    @property
    def available_stock(self):
        """Current physical stock minus items reserved in checkout."""
        return max(0, self.stock_quantity - self.reserved_quantity)

    @property
    def status(self):
        avail = self.available_stock
        if avail <= 0:
            return self.StockStatus.OUT_OF_STOCK
        elif avail <= self.low_stock_threshold:
            return self.StockStatus.LOW_STOCK
        return self.StockStatus.IN_STOCK

    @property
    def is_in_stock(self):
        return self.available_stock > 0


class InventoryHistory(TimeStampedModel):
    """
    Audit log of all stock movements and adjustments.
    """
    class ChangeReason(models.TextChoices):
        RESTOCK = 'restock', 'Manual Restock'
        PURCHASE = 'purchase', 'Order Placed'
        CANCELLED_ORDER = 'cancelled', 'Order Cancelled'
        RETURN = 'return', 'Customer Return'
        DAMAGE = 'damage', 'Damaged / Lost Goods'
        AUDIT = 'audit', 'Stock Audit Correction'

    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='history',
    )
    reason = models.CharField(
        max_length=30,
        choices=ChangeReason.choices,
        default=ChangeReason.RESTOCK,
    )
    quantity_change = models.IntegerField(help_text="Positive for additions, negative for deductions")
    previous_stock = models.PositiveIntegerField()
    new_stock = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_adjustments',
    )

    class Meta:
        verbose_name = 'Inventory History'
        verbose_name_plural = 'Inventory Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.inventory.variant.sku}: {self.quantity_change} ({self.reason})"

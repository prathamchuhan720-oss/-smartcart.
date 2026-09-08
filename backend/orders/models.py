"""
Order and OrderItem models for SmartCart orders app.
"""
import uuid
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from core.models import TimeStampedModel
from products.models import Product, ProductVariant
from accounts.models import Address
from coupons.models import Coupon


class Order(TimeStampedModel):
    """
    Customer orders with complete lifecycle and snapshot of prices & addresses.
    """
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        OUT_FOR_DELIVERY = 'out_for_delivery', 'Out for Delivery'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'
        RETURNED = 'returned', 'Returned'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
    )
    status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True,
    )
    payment_status = models.CharField(
        max_length=30,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
    )

    # Historical address snapshot stored as JSON or referenced FK
    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipping_orders',
    )
    shipping_address_snapshot = models.JSONField(
        default=dict,
        help_text="Immutable snapshot of shipping address at time of order",
    )

    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    tracking_number = models.CharField(max_length=100, blank=True)
    carrier = models.CharField(max_length=100, blank=True)
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at', 'status']),
        ]

    def __str__(self):
        return f"Order #{self.order_number} ({self.status}) - ₹{self.total_amount}"

    @classmethod
    def generate_order_number(cls):
        """Generate unique human-readable order number, e.g. ORD-20260908-AB12"""
        import datetime
        date_str = datetime.date.today().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:6].upper()
        return f"ORD-{date_str}-{unique_suffix}"

    @property
    def can_cancel(self):
        return self.status in [self.OrderStatus.PENDING, self.OrderStatus.CONFIRMED]


class OrderItem(TimeStampedModel):
    """
    Line items within an Order preserving historic product information and prices.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items',
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
    )
    product_name = models.CharField(max_length=255)
    variant_title = models.CharField(max_length=150, blank=True)
    sku = models.CharField(max_length=100)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Historical price paid per item",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.quantity}x {self.product_name} in #{self.order.order_number}"

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

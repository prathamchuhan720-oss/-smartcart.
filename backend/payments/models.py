"""
Payment model for SmartCart payments app.
"""
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from core.models import TimeStampedModel
from orders.models import Order


class Payment(TimeStampedModel):
    """
    Payment transactions supporting Razorpay sandbox, COD, and Mock.
    """
    class PaymentMethod(models.TextChoices):
        RAZORPAY = 'razorpay', 'Razorpay'
        COD = 'cod', 'Cash on Delivery'
        MOCK = 'mock', 'Test / Mock Sandbox'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
    )
    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.RAZORPAY,
    )
    transaction_id = models.CharField(max_length=150, unique=True, db_index=True)
    razorpay_order_id = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    razorpay_payment_id = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    currency = models.CharField(max_length=10, default='INR')
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
    )

    error_code = models.CharField(max_length=100, blank=True)
    error_description = models.TextField(blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment #{self.transaction_id} - ₹{self.amount} ({self.status})"

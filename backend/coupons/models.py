"""
Coupon and CouponUsage models for SmartCart coupons app.
"""
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from core.models import TimeStampedModel


class Coupon(TimeStampedModel):
    """
    Coupons for fixed or percentage discounts.
    """
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', 'Percentage'
        FIXED = 'fixed', 'Fixed Amount'

    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE,
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Capped maximum discount for percentage coupons",
    )
    start_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total number of times this coupon can be used across all users",
    )
    times_used = models.PositiveIntegerField(default=0)
    per_user_limit = models.PositiveIntegerField(
        default=1,
        help_text="Max times a single user can redeem this coupon",
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({self.discount_value}{'%' if self.discount_type == self.DiscountType.PERCENTAGE else ' ₹'})"

    def is_valid_for(self, user, order_amount):
        """
        Validates coupon against dates, status, limits, and order subtotal.
        Returns: (is_valid: bool, error_message: str or None)
        """
        now = timezone.now()
        if not self.is_active:
            return False, "This coupon is currently inactive."
        if now < self.start_date:
            return False, "This coupon offer has not started yet."
        if now > self.expiry_date:
            return False, "This coupon has expired."
        if self.usage_limit is not None and self.times_used >= self.usage_limit:
            return False, "This coupon has reached its maximum global usage limit."
        if order_amount < self.min_order_amount:
            return False, f"Minimum order amount of ₹{self.min_order_amount} required to use this coupon."

        if user and user.is_authenticated:
            user_used_count = self.usages.filter(user=user).count()
            if user_used_count >= self.per_user_limit:
                return False, f"You have already used this coupon the maximum allowed ({self.per_user_limit}) times."

        return True, None

    def calculate_discount(self, order_amount):
        """
        Calculates the applicable discount for an order amount.
        """
        if self.discount_type == self.DiscountType.PERCENTAGE:
            discount = (order_amount * self.discount_value) / Decimal('100.00')
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return round(discount, 2)
        elif self.discount_type == self.DiscountType.FIXED:
            return min(self.discount_value, order_amount)
        return Decimal('0.00')


class CouponUsage(TimeStampedModel):
    """
    Tracks usage of coupons by users per order.
    """
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name='usages',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coupon_usages',
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='coupon_usages',
        null=True,
        blank=True,
    )
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Coupon Usage'
        verbose_name_plural = 'Coupon Usages'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} used {self.coupon.code}"

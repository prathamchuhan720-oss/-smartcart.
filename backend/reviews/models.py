"""
Review model for SmartCart reviews app.
"""
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg, Count
from core.models import TimeStampedModel
from products.models import Product


class Review(TimeStampedModel):
    """
    Product reviews and ratings submitted by customers.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating between 1 and 5 stars",
    )
    title = models.CharField(max_length=150, blank=True)
    comment = models.TextField()
    is_approved = models.BooleanField(default=True, db_index=True)
    is_verified_purchase = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ['user', 'product']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'is_approved']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"{self.rating}★ review by {self.user.email} on {self.product.name}"

    def update_product_rating(self):
        """
        Recalculates and updates the product's average rating and total reviews.
        """
        approved_reviews = Review.objects.filter(product=self.product, is_approved=True)
        stats = approved_reviews.aggregate(avg=Avg('rating'), count=Count('id'))
        self.product.average_rating = round(stats['avg'] or 0.0, 2)
        self.product.total_reviews = stats['count'] or 0
        self.product.save(update_fields=['average_rating', 'total_reviews'])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_product_rating()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        # Update ratings after deletion
        approved_reviews = Review.objects.filter(product=product, is_approved=True)
        stats = approved_reviews.aggregate(avg=Avg('rating'), count=Count('id'))
        product.average_rating = round(stats['avg'] or 0.0, 2)
        product.total_reviews = stats['count'] or 0
        product.save(update_fields=['average_rating', 'total_reviews'])

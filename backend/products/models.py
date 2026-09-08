"""
Product, ProductImage, and ProductVariant models for SmartCart products app.
"""
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify
from core.models import TimeStampedModel
from categories.models import Category, Brand


class Product(TimeStampedModel):
    """
    Main Product catalog model.
    """
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=280, unique=True, db_index=True)
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
    )
    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
    )
    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        db_index=True,
    )
    total_reviews = models.PositiveIntegerField(default=0)

    image_url = models.URLField(max_length=500, blank=True, help_text="Direct CDN image URL")

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['base_price', 'average_rating']),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def final_price(self):
        """Calculates effective price after discount percentage."""
        if self.discount_percentage > Decimal('0.00'):
            discount_amount = (self.base_price * self.discount_percentage) / Decimal('100.00')
            return round(self.base_price - discount_amount, 2)
        return self.base_price

    @property
    def primary_image(self):
        primary = self.images.filter(is_primary=True).first()
        if primary:
            if primary.image:
                return primary.image.url
            if primary.image_url:
                return primary.image_url
        first_img = self.images.first()
        if first_img:
            if first_img.image:
                return first_img.image.url
            if first_img.image_url:
                return first_img.image_url
        return self.image_url if self.image_url else None

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ProductImage(TimeStampedModel):
    """
    Multiple images per product with primary image designation.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['sort_order', '-is_primary', '-created_at']

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariant(TimeStampedModel):
    """
    Product variant representing specific size, color combinations.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
    )
    title = models.CharField(max_length=150, help_text="e.g. Medium / Black")
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    size = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    color_code = models.CharField(max_length=10, blank=True, help_text="Hex code e.g. #000000")
    additional_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Added to product base price",
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
        unique_together = ['product', 'size', 'color']
        ordering = ['title']

    def __str__(self):
        return f"{self.product.name} - {self.title}"

    @property
    def price(self):
        return self.product.final_price + self.additional_price

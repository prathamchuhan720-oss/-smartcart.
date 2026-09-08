"""
Category and Brand models for SmartCart categories app.
"""
from django.db import models
from django.utils.text import slugify
from core.models import TimeStampedModel


class Category(TimeStampedModel):
    """
    Product Category model supporting hierarchical tree structure.
    """
    name = models.CharField(max_length=150, unique=True, db_index=True)
    slug = models.SlugField(max_length=170, unique=True, db_index=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
    )
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Icon class or name, e.g. fa-laptop')
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug', 'is_active']),
        ]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} -> {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(TimeStampedModel):
    """
    Brand or Manufacturer model.
    """
    name = models.CharField(max_length=150, unique=True, db_index=True)
    slug = models.SlugField(max_length=170, unique=True, db_index=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug', 'is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

from django.contrib import admin
from .models import Product, ProductImage, ProductVariant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'sort_order']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['title', 'sku', 'size', 'color', 'color_code', 'additional_price', 'is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'brand', 'base_price', 'discount_percentage', 'is_active', 'is_featured', 'average_rating']
    list_filter = ['is_active', 'is_featured', 'category', 'brand']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['title', 'sku', 'product', 'size', 'color', 'additional_price', 'is_active']
    list_filter = ['is_active', 'size', 'color']
    search_fields = ['title', 'sku', 'product__name']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_primary', 'sort_order', 'created_at']
    list_filter = ['is_primary']
    search_fields = ['product__name', 'alt_text']

from rest_framework import serializers
from .models import Product, ProductImage, ProductVariant
from categories.serializers import CategorySerializer, BrandSerializer
from inventory.models import Inventory


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'sort_order']


class ProductVariantSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    stock_quantity = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'title', 'sku', 'size', 'color', 'color_code',
            'additional_price', 'price', 'is_active', 'stock_quantity',
            'stock_status', 'is_in_stock',
        ]

    def get_stock_quantity(self, obj):
        if hasattr(obj, 'inventory'):
            return obj.inventory.available_stock
        return 0

    def get_stock_status(self, obj):
        if hasattr(obj, 'inventory'):
            return obj.inventory.status
        return 'out_of_stock'

    def get_is_in_stock(self, obj):
        if hasattr(obj, 'inventory'):
            return obj.inventory.is_in_stock
        return False


class ProductListSerializer(serializers.ModelSerializer):
    """Compact serializer for product list/grid views."""
    category_name = serializers.ReadOnlyField(source='category.name')
    brand_name = serializers.ReadOnlyField(source='brand.name')
    final_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    primary_image = serializers.ReadOnlyField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'category', 'category_name',
            'brand', 'brand_name', 'base_price', 'discount_percentage',
            'final_price', 'primary_image', 'average_rating', 'total_reviews',
            'is_active', 'is_featured', 'in_stock', 'created_at',
        ]

    def get_in_stock(self, obj):
        return any(
            v.inventory.is_in_stock for v in obj.variants.all() if hasattr(v, 'inventory')
        )


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for product detail page with images, variants, and inventory."""
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Product._meta.get_field('category').remote_field.model.objects.all(),
        write_only=True
    )
    brand_id = serializers.PrimaryKeyRelatedField(
        source='brand',
        queryset=Product._meta.get_field('brand').remote_field.model.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    final_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    primary_image = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'description', 'image_url',
            'category', 'category_id', 'brand', 'brand_id',
            'base_price', 'discount_percentage', 'final_price',
            'images', 'variants', 'primary_image', 'average_rating',
            'total_reviews', 'is_active', 'is_featured', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'average_rating', 'total_reviews', 'created_at', 'updated_at']

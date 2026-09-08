from decimal import Decimal
from rest_framework import serializers
from .models import Cart, CartItem
from products.models import ProductVariant


class CartItemVariantSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_slug = serializers.ReadOnlyField(source='product.slug')
    product_image = serializers.ReadOnlyField(source='product.primary_image')
    price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    available_stock = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'title', 'sku', 'size', 'color', 'price',
            'product_name', 'product_slug', 'product_image', 'available_stock'
        ]

    def get_available_stock(self, obj):
        if hasattr(obj, 'inventory'):
            return obj.inventory.available_stock
        return 0


class CartItemSerializer(serializers.ModelSerializer):
    variant = CartItemVariantSerializer(read_only=True)
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.filter(is_active=True),
        source='variant',
        write_only=True
    )
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'variant', 'variant_id', 'quantity', 'subtotal', 'created_at', 'updated_at']
        read_only_fields = ['id', 'subtotal', 'created_at', 'updated_at']

    def validate(self, attrs):
        variant = attrs.get('variant')
        quantity = attrs.get('quantity', 1)

        if variant and hasattr(variant, 'inventory'):
            if variant.inventory.available_stock < quantity:
                raise serializers.ValidationError({
                    'quantity': f"Only {variant.inventory.available_stock} item(s) available in stock."
                })
        return attrs


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'subtotal', 'created_at', 'updated_at']
        read_only_fields = ['id', 'subtotal', 'total_items', 'created_at', 'updated_at']

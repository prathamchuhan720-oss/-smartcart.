from rest_framework import serializers
from .models import Inventory, InventoryHistory
from products.models import ProductVariant


class InventoryHistorySerializer(serializers.ModelSerializer):
    performed_by_email = serializers.ReadOnlyField(source='performed_by.email')

    class Meta:
        model = InventoryHistory
        fields = [
            'id', 'reason', 'quantity_change', 'previous_stock',
            'new_stock', 'notes', 'performed_by_email', 'created_at',
        ]


class InventorySerializer(serializers.ModelSerializer):
    variant_title = serializers.ReadOnlyField(source='variant.title')
    variant_sku = serializers.ReadOnlyField(source='variant.sku')
    product_name = serializers.ReadOnlyField(source='variant.product.name')
    product_slug = serializers.ReadOnlyField(source='variant.product.slug')
    product_image = serializers.ReadOnlyField(source='variant.product.primary_image')
    available_stock = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()
    history = InventoryHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Inventory
        fields = [
            'id', 'variant', 'variant_title', 'variant_sku',
            'product_name', 'product_slug', 'product_image',
            'stock_quantity', 'reserved_quantity', 'available_stock',
            'low_stock_threshold', 'status', 'history', 'updated_at',
        ]
        read_only_fields = ['id', 'variant', 'reserved_quantity', 'updated_at']


class StockAdjustmentSerializer(serializers.Serializer):
    quantity_change = serializers.IntegerField(required=True)
    reason = serializers.ChoiceField(choices=InventoryHistory.ChangeReason.choices, default=InventoryHistory.ChangeReason.RESTOCK)
    notes = serializers.CharField(required=False, allow_blank=True)

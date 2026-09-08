from rest_framework import serializers
from .models import Order, OrderItem
from accounts.models import Address
from accounts.serializers import AddressSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'variant', 'product_name', 'variant_title',
            'sku', 'unit_price', 'quantity', 'subtotal',
        ]
        read_only_fields = ['id', 'unit_price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_email = serializers.ReadOnlyField(source='user.email')
    customer_name = serializers.ReadOnlyField(source='user.full_name')
    can_cancel = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'customer_email', 'customer_name',
            'status', 'payment_status', 'shipping_address', 'shipping_address_snapshot',
            'subtotal', 'discount_amount', 'shipping_fee', 'tax_amount',
            'total_amount', 'tracking_number', 'carrier', 'customer_notes',
            'admin_notes', 'can_cancel', 'items', 'created_at', 'delivered_at', 'cancelled_at',
        ]
        read_only_fields = [
            'id', 'order_number', 'user', 'subtotal', 'discount_amount',
            'shipping_fee', 'tax_amount', 'total_amount', 'shipping_address_snapshot',
            'created_at', 'delivered_at', 'cancelled_at',
        ]


class CheckoutSerializer(serializers.Serializer):
    shipping_address_id = serializers.IntegerField(required=True)
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    customer_notes = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=['razorpay', 'cod', 'mock'], default='razorpay')

from rest_framework import serializers
from .models import Coupon, CouponUsage


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'discount_type', 'discount_value',
            'min_order_amount', 'max_discount_amount', 'start_date', 'expiry_date',
            'usage_limit', 'times_used', 'per_user_limit', 'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'times_used', 'created_at']


class CouponValidateSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    order_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)

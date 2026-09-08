from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'transaction_id', 'payment_method',
            'razorpay_order_id', 'razorpay_payment_id', 'amount',
            'currency', 'status', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class CreatePaymentRequestSerializer(serializers.Serializer):
    order_number = serializers.CharField(required=True)


class VerifyPaymentSerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField(required=False, allow_blank=True)
    razorpay_payment_id = serializers.CharField(required=True)
    razorpay_signature = serializers.CharField(required=False, allow_blank=True)
    transaction_id = serializers.CharField(required=True)

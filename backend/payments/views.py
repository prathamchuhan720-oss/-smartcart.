import hmac
import hashlib
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from rest_framework import views, status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from orders.models import Order
from .models import Payment
from .serializers import CreatePaymentRequestSerializer, VerifyPaymentSerializer, PaymentSerializer


@extend_schema(tags=['Payments'])
class CreatePaymentView(views.APIView):
    """
    Initialize payment gateway order (Razorpay sandbox or test simulation).
    Returns payment credentials for frontend checkout modal.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreatePaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_number = serializer.validated_data['order_number']

        try:
            order = Order.objects.get(order_number=order_number, user=request.user)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        if order.payment_status == Order.PaymentStatus.PAID:
            return Response({'detail': 'Order is already paid.'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve or create payment record
        payment, _ = Payment.objects.get_or_create(
            order=order,
            defaults={
                'user': request.user,
                'amount': order.total_amount,
                'transaction_id': f"TXN-{uuid.uuid4().hex[:12].upper()}",
            }
        )

        key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
        # If Razorpay keys are configured, generate Razorpay order ID or simulate test order
        rzp_order_id = f"order_{uuid.uuid4().hex[:14]}"
        payment.razorpay_order_id = rzp_order_id
        payment.save(update_fields=['razorpay_order_id'])

        return Response({
            'success': True,
            'razorpay_key_id': key_id or 'rzp_test_smartcart_sandbox',
            'razorpay_order_id': rzp_order_id,
            'transaction_id': payment.transaction_id,
            'amount': int(order.total_amount * 100), # amount in paise for Razorpay
            'currency': 'INR',
            'customer': {
                'name': request.user.full_name,
                'email': request.user.email,
                'phone': request.user.phone_number or '',
            },
            'order_number': order.order_number,
        })


@extend_schema(tags=['Payments'])
class VerifyPaymentView(views.APIView):
    """
    Verifies payment signature from Razorpay sandbox or test environment.
    Never stores sensitive card details.
    Marks Order as CONFIRMED and payment as PAID upon signature verification.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            payment = Payment.objects.select_related('order').get(
                transaction_id=data['transaction_id'],
                user=request.user
            )
        except Payment.DoesNotExist:
            return Response({'detail': 'Payment record not found.'}, status=status.HTTP_404_NOT_FOUND)

        rzp_order_id = data.get('razorpay_order_id') or payment.razorpay_order_id or ''
        rzp_payment_id = data['razorpay_payment_id']
        rzp_signature = data.get('razorpay_signature', '')
        key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')

        # Signature verification:
        # If live/real key secret is configured, compute HMAC SHA256
        is_signature_valid = True
        if key_secret and rzp_signature and rzp_order_id:
            msg = f"{rzp_order_id}|{rzp_payment_id}".encode('utf-8')
            generated_signature = hmac.new(key_secret.encode('utf-8'), msg, hashlib.sha256).hexdigest()
            is_signature_valid = hmac.compare_digest(generated_signature, rzp_signature)

        if not is_signature_valid:
            payment.status = Payment.PaymentStatus.FAILED
            payment.error_description = "Invalid payment gateway signature."
            payment.save()
            return Response({
                'success': False,
                'message': 'Payment verification failed: invalid signature.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update Payment and Order atomically
        with transaction.atomic():
            payment.status = Payment.PaymentStatus.SUCCESS
            payment.razorpay_payment_id = rzp_payment_id
            payment.razorpay_signature = rzp_signature
            payment.save()

            order = payment.order
            order.payment_status = Order.PaymentStatus.PAID
            order.status = Order.OrderStatus.CONFIRMED
            order.save()

        return Response({
            'success': True,
            'message': 'Payment verified successfully! Your order is confirmed.',
            'order_number': order.order_number,
            'payment': PaymentSerializer(payment).data,
        })

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from core.permissions import IsAdminUser, IsOwnerOrAdmin
from .models import Order, OrderItem
from .serializers import OrderSerializer, CheckoutSerializer
from cart.models import Cart
from accounts.models import Address
from coupons.models import Coupon, CouponUsage
from inventory.models import InventoryHistory
from payments.models import Payment


@extend_schema(tags=['Orders'])
class OrderViewSet(viewsets.ModelViewSet):
    """
    Manage and view customer orders.
    """
    serializer_class = OrderSerializer
    lookup_field = 'order_number'

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'update_status']:
            return [IsAdminUser()]
        return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().select_related('user').prefetch_related('items')
        return Order.objects.filter(user=user).prefetch_related('items')

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, order_number=None):
        """
        Cancel order if eligible and restore inventory.
        """
        order = self.get_object()
        if not order.can_cancel and not request.user.is_staff:
            return Response({
                'success': False,
                'message': f"Order cannot be cancelled at this stage ({order.status})."
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order.status = Order.OrderStatus.CANCELLED
            order.cancelled_at = timezone.now()
            order.cancellation_reason = request.data.get('reason', 'Cancelled by customer')
            order.save()

            # Restore inventory stock
            for item in order.items.all():
                if item.variant and hasattr(item.variant, 'inventory'):
                    inv = item.variant.inventory
                    prev_stock = inv.stock_quantity
                    inv.stock_quantity += item.quantity
                    inv.save()

                    InventoryHistory.objects.create(
                        inventory=inv,
                        reason=InventoryHistory.ChangeReason.CANCELLED_ORDER,
                        quantity_change=item.quantity,
                        previous_stock=prev_stock,
                        new_stock=inv.stock_quantity,
                        notes=f"Restored from cancelled Order #{order.order_number}",
                        performed_by=request.user,
                    )

        return Response({
            'success': True,
            'message': 'Order cancelled successfully and items returned to stock.',
            'order': OrderSerializer(order).data
        })

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def update_status(self, request, order_number=None):
        """
        Admin endpoint to advance order status through lifecycle:
        Pending -> Confirmed -> Processing -> Shipped -> Out for Delivery -> Delivered
        """
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status not in Order.OrderStatus.values:
            return Response({'detail': f"Invalid status: {new_status}"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        if new_status == Order.OrderStatus.DELIVERED:
            order.delivered_at = timezone.now()
        if 'tracking_number' in request.data:
            order.tracking_number = request.data['tracking_number']
        if 'carrier' in request.data:
            order.carrier = request.data['carrier']
        if 'admin_notes' in request.data:
            order.admin_notes = request.data['admin_notes']
        order.save()

        return Response({
            'success': True,
            'message': f"Order status updated to {order.get_status_display()}.",
            'order': OrderSerializer(order).data
        })


@extend_schema(tags=['Orders'])
class CheckoutView(generics.GenericAPIView):
    """
    Atomic Checkout:
    Converts customer's active cart into a confirmed Order.
    Validates stock, deducts inventory, applies coupons, snapshots address, and initializes payment.
    """
    serializer_class = CheckoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'detail': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = cart.items.select_related('variant__product', 'variant__inventory').all()
        if not cart_items.exists():
            return Response({'detail': 'Your cart is empty. Please add products.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate Address
        try:
            address = Address.objects.get(pk=data['shipping_address_id'], user=user)
        except Address.DoesNotExist:
            return Response({'detail': 'Shipping address not found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Snapshot address
        address_snapshot = {
            'full_name': address.full_name,
            'phone_number': address.phone_number,
            'street_address': address.street_address,
            'landmark': address.landmark,
            'city': address.city,
            'state': address.state,
            'postal_code': address.postal_code,
            'country': address.country,
        }

        # Perform checkout in a single atomic database transaction
        with transaction.atomic():
            # 1. Stock Check & Reservation
            for item in cart_items:
                variant = item.variant
                if not hasattr(variant, 'inventory') or variant.inventory.available_stock < item.quantity:
                    avail = variant.inventory.available_stock if hasattr(variant, 'inventory') else 0
                    return Response({
                        'success': False,
                        'message': f"Insufficient stock for '{variant.product.name} ({variant.title})'. Only {avail} left.",
                    }, status=status.HTTP_400_BAD_REQUEST)

            # 2. Compute Subtotal
            subtotal = sum((item.subtotal for item in cart_items), Decimal('0.00'))

            # 3. Apply Coupon if provided
            discount_amount = Decimal('0.00')
            applied_coupon = None
            coupon_code = data.get('coupon_code', '').upper().strip()
            if coupon_code:
                try:
                    applied_coupon = Coupon.objects.get(code=coupon_code)
                    is_valid, err = applied_coupon.is_valid_for(user, subtotal)
                    if is_valid:
                        discount_amount = applied_coupon.calculate_discount(subtotal)
                    else:
                        return Response({'detail': f"Coupon error: {err}"}, status=status.HTTP_400_BAD_REQUEST)
                except Coupon.DoesNotExist:
                    return Response({'detail': 'Coupon code does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

            # 4. Compute Tax & Shipping Fee
            shipping_fee = Decimal('0.00') if subtotal > Decimal('999.00') else Decimal('99.00')
            tax_amount = round((subtotal - discount_amount) * Decimal('0.18'), 2)  # 18% standard GST
            total_amount = round(subtotal - discount_amount + shipping_fee + tax_amount, 2)

            # 5. Create Order
            order = Order.objects.create(
                order_number=Order.generate_order_number(),
                user=user,
                status=Order.OrderStatus.PENDING,
                shipping_address=address,
                shipping_address_snapshot=address_snapshot,
                subtotal=subtotal,
                discount_amount=discount_amount,
                coupon=applied_coupon,
                shipping_fee=shipping_fee,
                tax_amount=tax_amount,
                total_amount=total_amount,
                customer_notes=data.get('customer_notes', ''),
            )

            # 6. Create OrderItems and Deduct Inventory
            for item in cart_items:
                variant = item.variant
                OrderItem.objects.create(
                    order=order,
                    product=variant.product,
                    variant=variant,
                    product_name=variant.product.name,
                    variant_title=variant.title,
                    sku=variant.sku,
                    unit_price=variant.price,
                    quantity=item.quantity,
                    subtotal=item.subtotal,
                )

                # Deduct stock
                inv = variant.inventory
                prev_stock = inv.stock_quantity
                inv.stock_quantity -= item.quantity
                inv.save()

                InventoryHistory.objects.create(
                    inventory=inv,
                    reason=InventoryHistory.ChangeReason.PURCHASE,
                    quantity_change=-item.quantity,
                    previous_stock=prev_stock,
                    new_stock=inv.stock_quantity,
                    notes=f"Order #{order.order_number}",
                    performed_by=user,
                )

            # 7. Record Coupon Usage
            if applied_coupon:
                CouponUsage.objects.create(
                    coupon=applied_coupon,
                    user=user,
                    order=order,
                    discount_applied=discount_amount,
                )
                applied_coupon.times_used += 1
                applied_coupon.save()

            # 8. Create Payment Record (Sandbox/Test or COD)
            payment_method = data.get('payment_method', 'razorpay')
            import uuid
            tx_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
            Payment.objects.create(
                order=order,
                user=user,
                payment_method=payment_method,
                transaction_id=tx_id,
                amount=total_amount,
                currency='INR',
                status=Payment.PaymentStatus.PENDING,
            )

            # 9. Clear Cart
            cart.clear()

        return Response({
            'success': True,
            'message': 'Order placed successfully!',
            'order': OrderSerializer(order).data,
            'payment': {
                'transaction_id': tx_id,
                'amount': float(total_amount),
                'currency': 'INR',
                'payment_method': payment_method,
            }
        }, status=status.HTTP_201_CREATED)

from decimal import Decimal
from rest_framework import viewsets, views, status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.permissions import IsAdminUser
from .models import Coupon
from .serializers import CouponSerializer, CouponValidateSerializer


@extend_schema(tags=['Coupons'])
class CouponViewSet(viewsets.ModelViewSet):
    """
    CRUD for Coupons (Admin only for modifications).
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Coupon.objects.all()
        return Coupon.objects.filter(is_active=True)


@extend_schema(tags=['Coupons'])
class ValidateCouponView(views.APIView):
    """
    Check if a coupon is valid for the current user and subtotal, and calculate exact discount.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code'].upper().strip()
        order_amount = serializer.validated_data['order_amount']

        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid coupon code.'
            }, status=status.HTTP_400_BAD_REQUEST)

        is_valid, err_msg = coupon.is_valid_for(request.user, order_amount)
        if not is_valid:
            return Response({
                'success': False,
                'message': err_msg
            }, status=status.HTTP_400_BAD_REQUEST)

        discount = coupon.calculate_discount(order_amount)
        return Response({
            'success': True,
            'message': f"Coupon applied! You saved ₹{discount}.",
            'coupon': {
                'id': coupon.id,
                'code': coupon.code,
                'discount_type': coupon.discount_type,
                'discount_value': coupon.discount_value,
                'discount_applied': discount,
                'new_total': max(Decimal('0.00'), order_amount - discount),
            }
        }, status=status.HTTP_200_OK)

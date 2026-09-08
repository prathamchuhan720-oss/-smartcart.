from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from core.permissions import IsAdminUser
from .models import Inventory, InventoryHistory
from .serializers import InventorySerializer, StockAdjustmentSerializer


@extend_schema(tags=['Inventory'])
class InventoryViewSet(viewsets.ModelViewSet):
    """
    Inventory management endpoints (Admin only).
    """
    queryset = Inventory.objects.select_related('variant__product').prefetch_related('history').all()
    serializer_class = InventorySerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """List products with inventory at or below their low-stock threshold."""
        low_stock_items = self.queryset.filter(
            stock_quantity__gt=0,
            stock_quantity__lte=F('low_stock_threshold')
        )
        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """List items that are completely out of stock."""
        out_items = self.queryset.filter(stock_quantity=0)
        serializer = self.get_serializer(out_items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """
        Adjust stock quantity (positive to restock, negative to reduce) with audit reason.
        """
        inventory = self.get_object()
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        change = serializer.validated_data['quantity_change']
        reason = serializer.validated_data['reason']
        notes = serializer.validated_data.get('notes', '')

        with transaction.atomic():
            prev_stock = inventory.stock_quantity
            new_stock = prev_stock + change
            if new_stock < 0:
                return Response({
                    'detail': f"Cannot reduce stock below 0. Current stock is {prev_stock}."
                }, status=status.HTTP_400_BAD_REQUEST)

            inventory.stock_quantity = new_stock
            inventory.save()

            history = InventoryHistory.objects.create(
                inventory=inventory,
                reason=reason,
                quantity_change=change,
                previous_stock=prev_stock,
                new_stock=new_stock,
                notes=notes,
                performed_by=request.user,
            )

        return Response({
            'message': f"Stock adjusted from {prev_stock} to {new_stock}.",
            'inventory': InventorySerializer(inventory).data
        })

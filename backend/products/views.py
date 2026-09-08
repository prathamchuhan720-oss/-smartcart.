from django.db.models import Count, Q
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter

from inventory.models import Inventory
from core.permissions import IsAdminUser
from .models import Product, ProductImage, ProductVariant
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductImageSerializer,
    ProductVariantSerializer,
)
from .filters import ProductFilter


@extend_schema(tags=['Products'])
class ProductViewSet(viewsets.ModelViewSet):
    """
    Catalog endpoint providing product listings, search, filtering, and recommendations.
    """
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'sku', 'brand__name', 'category__name']
    ordering_fields = ['base_price', 'average_rating', 'created_at', 'total_reviews']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'add_image', 'add_variant']:
            return [IsAdminUser()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'create', 'update', 'partial_update']:
            return ProductDetailSerializer
        return ProductListSerializer

    def get_queryset(self):
        queryset = Product.objects.select_related('category', 'brand').prefetch_related(
            'images',
            'variants__inventory'
        )
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset

    def perform_create(self, serializer):
        product = serializer.save()
        # Automatically create default variant and inventory if none exist
        if not product.variants.exists():
            variant = ProductVariant.objects.create(
                product=product,
                title="Standard",
                sku=f"{product.sku}-STD",
                size="Standard",
                color="Default",
            )
            initial_stock = int(self.request.data.get('initial_stock', 20))
            Inventory.objects.create(
                variant=variant,
                stock_quantity=initial_stock,
                low_stock_threshold=5,
            )

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def recommendations(self, request, slug=None):
        """
        Rule-Based Recommendation Engine:
        Recommends products from the same category or brand, sorted by rating and popularity.
        Extensible for machine learning collaborative filtering in the future.
        """
        product = self.get_object()
        similar = Product.objects.filter(
            Q(category=product.category) | Q(brand=product.brand),
            is_active=True,
        ).exclude(pk=product.pk).order_by('-average_rating', '-total_reviews')[:6]

        serializer = ProductListSerializer(similar, many=True)
        return Response({
            'success': True,
            'source_product': product.name,
            'recommendations': serializer.data
        })

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def featured(self, request):
        """Get featured products."""
        featured = self.get_queryset().filter(is_featured=True)[:8]
        serializer = ProductListSerializer(featured, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def add_image(self, request, slug=None):
        """Admin can upload an image for this product."""
        product = self.get_object()
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def add_variant(self, request, slug=None):
        """Admin can add a variant for this product."""
        product = self.get_object()
        serializer = ProductVariantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

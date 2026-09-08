from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.permissions import IsAdminUser
from .models import Category, Brand
from .serializers import CategorySerializer, CategoryTreeSerializer, BrandSerializer


@extend_schema(tags=['Categories'])
class CategoryViewSet(viewsets.ModelViewSet):
    """
    Endpoints for browsing and managing product categories.
    """
    queryset = Category.objects.all()
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action == 'tree':
            return CategoryTreeSerializer
        return CategorySerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Category.objects.all().select_related('parent')
        return Category.objects.filter(is_active=True).select_related('parent')

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def tree(self, request):
        """Get full hierarchical tree of top-level categories with children."""
        top_categories = Category.objects.filter(parent__isnull=True, is_active=True)
        serializer = CategoryTreeSerializer(top_categories, many=True)
        return Response(serializer.data)


@extend_schema(tags=['Categories'])
class BrandViewSet(viewsets.ModelViewSet):
    """
    Endpoints for browsing and managing product brands.
    """
    queryset = Brand.objects.all()
    lookup_field = 'slug'
    serializer_class = BrandSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Brand.objects.all()
        return Brand.objects.filter(is_active=True)

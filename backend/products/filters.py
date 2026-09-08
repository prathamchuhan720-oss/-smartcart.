import django_filters
from django.db.models import Q
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Comprehensive filter for product catalog:
    - category: category slug or id
    - brand: brand slug or id
    - min_price: base price minimum
    - max_price: base price maximum
    - min_rating: minimum average rating
    - in_stock: true/false
    - is_featured: true/false
    """
    category = django_filters.CharFilter(method='filter_category')
    brand = django_filters.CharFilter(method='filter_brand')
    min_price = django_filters.NumberFilter(field_name='base_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='base_price', lookup_expr='lte')
    min_rating = django_filters.NumberFilter(field_name='average_rating', lookup_expr='gte')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['category', 'brand', 'min_price', 'max_price', 'min_rating', 'is_featured', 'is_active']

    def filter_category(self, queryset, name, value):
        if value.isdigit():
            return queryset.filter(Q(category_id=value) | Q(category__parent_id=value))
        return queryset.filter(Q(category__slug=value) | Q(category__parent__slug=value))

    def filter_brand(self, queryset, name, value):
        if value.isdigit():
            return queryset.filter(brand_id=value)
        return queryset.filter(brand__slug=value)

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(variants__inventory__stock_quantity__gt=0).distinct()
        return queryset

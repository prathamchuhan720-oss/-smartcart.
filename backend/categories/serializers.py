from rest_framework import serializers
from .models import Category, Brand


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Recursive serializer for nested category tree."""
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'image', 'is_active', 'parent', 'children']

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CategoryTreeSerializer(children, many=True).data


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.ReadOnlyField(source='parent.name')

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'image', 'parent', 'parent_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class BrandSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(source='products.count', read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description', 'logo', 'website', 'is_active', 'products_count', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']

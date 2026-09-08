from rest_framework import serializers
from .models import Review
from products.models import Product


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.full_name')
    user_email = serializers.ReadOnlyField(source='user.email')
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_name', 'user_email', 'product',
            'product_name', 'rating', 'title', 'comment',
            'is_approved', 'is_verified_purchase', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'is_approved', 'is_verified_purchase', 'created_at', 'updated_at']


class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be an integer between 1 and 5.")
        return value

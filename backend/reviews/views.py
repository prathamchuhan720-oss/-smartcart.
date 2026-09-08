from django.db.models import Count, Avg
from rest_framework import views, viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from core.permissions import IsAdminUser
from .models import Review
from .serializers import ReviewSerializer, CreateReviewSerializer
from products.models import Product
from orders.models import Order, OrderItem


@extend_schema(tags=['Reviews'])
class ProductReviewsView(views.APIView):
    """
    List approved reviews and statistics for a specific product, or submit a new review.
    """
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        reviews = Review.objects.filter(product=product, is_approved=True).select_related('user')
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for item in reviews.values('rating').annotate(total=Count('rating')):
            distribution[item['rating']] = item['total']

        return Response({
            'product_id': product.id,
            'average_rating': product.average_rating,
            'total_reviews': product.total_reviews,
            'rating_distribution': distribution,
            'reviews': ReviewSerializer(reviews, many=True).data,
        })

    def post(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        # Check if user already reviewed
        if Review.objects.filter(user=user, product=product).exists():
            return Response({
                'detail': 'You have already submitted a review for this product.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check verified purchase: user must have completed an order with this product
        has_purchased = OrderItem.objects.filter(
            order__user=user,
            product=product,
            order__payment_status=Order.PaymentStatus.PAID
        ).exists()

        serializer = CreateReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = Review.objects.create(
            user=user,
            product=product,
            rating=serializer.validated_data['rating'],
            title=serializer.validated_data.get('title', ''),
            comment=serializer.validated_data['comment'],
            is_verified_purchase=has_purchased,
            is_approved=True,  # Auto-approved or set False if admin moderation required
        )

        return Response({
            'success': True,
            'message': 'Review submitted successfully.',
            'review': ReviewSerializer(review).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Reviews'])
class AdminReviewViewSet(viewsets.ModelViewSet):
    """
    Admin moderation endpoint for reviews.
    """
    queryset = Review.objects.select_related('user', 'product').all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        review = self.get_object()
        review.is_approved = True
        review.save()
        return Response({'message': 'Review approved.', 'review': ReviewSerializer(review).data})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        review = self.get_object()
        review.is_approved = False
        review.save()
        return Response({'message': 'Review rejected/hidden.', 'review': ReviewSerializer(review).data})

from rest_framework import views, status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Wishlist, WishlistItem
from .serializers import WishlistSerializer, WishlistItemSerializer
from products.models import Product


@extend_schema(tags=['Wishlist'])
class WishlistView(views.APIView):
    """
    Get the authenticated customer's wishlist.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data)

    def post(self, request):
        """Add product to wishlist; duplicate additions are safely handled."""
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'detail': 'product_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
        if not created:
            return Response({'message': 'Product is already in your wishlist.'}, status=status.HTTP_200_OK)

        return Response({
            'message': 'Product added to wishlist.',
            'wishlist': WishlistSerializer(wishlist).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Wishlist'])
class WishlistItemDeleteView(views.APIView):
    """
    Remove product from customer's wishlist.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, product_id):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        deleted_count, _ = WishlistItem.objects.filter(wishlist=wishlist, product_id=product_id).delete()
        if deleted_count == 0:
            return Response({'detail': 'Item not in wishlist.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            'message': 'Product removed from wishlist.',
            'wishlist': WishlistSerializer(wishlist).data
        })

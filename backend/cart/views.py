from rest_framework import views, status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


def get_or_create_cart(request):
    """Retrieve or create the cart for authenticated user or anonymous session."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


@extend_schema(tags=['Cart'])
class CartView(views.APIView):
    """
    Get current customer shopping cart with items, quantities, and subtotal.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cart = get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


@extend_schema(tags=['Cart'])
class CartItemCreateView(views.APIView):
    """
    Add a product variant to cart with server-side stock validation.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        cart = get_or_create_cart(request)
        serializer = CartItemSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        variant = serializer.validated_data['variant']
        quantity = serializer.validated_data.get('quantity', 1)

        # Check if item already exists in cart
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={'quantity': quantity}
        )

        if not created:
            new_qty = item.quantity + quantity
            if hasattr(variant, 'inventory') and variant.inventory.available_stock < new_qty:
                return Response({
                    'success': False,
                    'message': 'Insufficient stock',
                    'errors': {'quantity': [f"Only {variant.inventory.available_stock} items available."]}
                }, status=status.HTTP_400_BAD_REQUEST)
            item.quantity = new_qty
            item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Cart'])
class CartItemDetailView(views.APIView):
    """
    Update quantity or remove an item from the cart.
    """
    permission_classes = [permissions.AllowAny]

    def patch(self, request, pk):
        cart = get_or_create_cart(request)
        try:
            item = cart.items.get(pk=pk)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found in your cart.'}, status=status.HTTP_404_NOT_FOUND)

        quantity = int(request.data.get('quantity', item.quantity))
        if quantity <= 0:
            item.delete()
        else:
            if hasattr(item.variant, 'inventory') and item.variant.inventory.available_stock < quantity:
                return Response({
                    'success': False,
                    'message': 'Insufficient stock',
                    'errors': {'quantity': [f"Only {item.variant.inventory.available_stock} available in stock."]}
                }, status=status.HTTP_400_BAD_REQUEST)
            item.quantity = quantity
            item.save()

        return Response(CartSerializer(cart).data)

    def delete(self, request, pk):
        cart = get_or_create_cart(request)
        try:
            item = cart.items.get(pk=pk)
            item.delete()
            return Response(CartSerializer(cart).data)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found in your cart.'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(tags=['Cart'])
class CartClearView(views.APIView):
    """
    Empty all items from the current cart.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        cart = get_or_create_cart(request)
        cart.clear()
        return Response({'message': 'Cart cleared successfully.', 'cart': CartSerializer(cart).data})

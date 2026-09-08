from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CheckoutView

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='order-checkout'),
    path('', include(router.urls)),
]

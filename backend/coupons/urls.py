from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CouponViewSet, ValidateCouponView

router = DefaultRouter()
router.register(r'', CouponViewSet, basename='coupon')

urlpatterns = [
    path('validate/', ValidateCouponView.as_view(), name='coupon-validate'),
    path('', include(router.urls)),
]

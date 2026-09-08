from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductReviewsView, AdminReviewViewSet

router = DefaultRouter()
router.register(r'admin', AdminReviewViewSet, basename='admin-review')

urlpatterns = [
    path('product/<int:product_id>/', ProductReviewsView.as_view(), name='product-reviews'),
    path('', include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, BrandViewSet

router = DefaultRouter()
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]

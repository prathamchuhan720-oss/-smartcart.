"""
URLs for accounts authentication, profiles, and addresses.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    ChangePasswordView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    AddressViewSet,
    AdminUserListView,
)

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('profile/', ProfileView.as_view(), name='auth-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='auth-password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('', include(router.urls)),
]

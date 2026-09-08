"""
Custom permission classes for SmartCart.

Provides role-based access control for DRF views.
"""
from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Allow access only to admin users.

    Checks both Django's is_staff flag and the custom role field
    (to be implemented in the User model).
    """
    message = 'Admin access required.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class IsCustomer(BasePermission):
    """
    Allow access only to authenticated customer users.
    """
    message = 'Customer access required.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and not request.user.is_staff
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission: allow access only to the owner of the
    object or admin users.

    Expects the object to have a ``user`` attribute.
    """
    message = 'You do not have permission to access this resource.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        # Check common owner field names
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'customer'):
            return obj.customer == request.user
        return False


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Allow read-only access to unauthenticated users,
    write access to authenticated users.
    """

    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return bool(request.user and request.user.is_authenticated)

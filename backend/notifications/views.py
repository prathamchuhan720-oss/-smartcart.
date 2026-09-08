from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Notification
from .serializers import NotificationSerializer


@extend_schema(tags=['Notifications'])
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List and mark read user notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Marked as read.'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'message': 'All notifications marked as read.'})

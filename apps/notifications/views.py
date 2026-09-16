from rest_framework import generics, permissions
from drf_yasg.utils import swagger_auto_schema

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    @swagger_auto_schema(
        tags=['Notifications'],
        operation_description='Return notifications belonging to the authenticated user.',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationDetailAPIView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    http_method_names = ['patch', 'head', 'options']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction

from .models import Notification
from .serializers import NotificationSerializer


logger = logging.getLogger(__name__)


def broadcast_notification(notification):
    """Send a persisted notification to the user's active WebSocket sessions."""
    payload = NotificationSerializer(notification).data
    group_name = f'notifications_user_{notification.user_id}'

    def send():
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            {'type': 'notification.message', 'notification': payload},
        )
        logger.info(
            'WebSocket notification broadcast: user_id=%s notification_id=%s kind=%s',
            notification.user_id,
            notification.pk,
            notification.kind,
        )

    transaction.on_commit(send)
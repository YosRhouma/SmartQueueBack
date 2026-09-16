import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer


logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            logger.warning('WebSocket notification rejected: invalid or missing JWT')
            await self.close(code=4401)
            return

        self.group_name = f'notifications_user_{user.pk}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info('WebSocket notification connected: user_id=%s', user.pk)

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.info('WebSocket notification disconnected: user_id=%s code=%s', self.scope['user'].pk, close_code)

    async def notification_message(self, event):
        await self.send_json(event['notification'])
        logger.info(
            'WebSocket notification sent: user_id=%s notification_id=%s kind=%s',
            self.scope['user'].pk,
            event['notification']['id'],
            event['notification']['kind'],
        )
import logging
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication


logger = logging.getLogger(__name__)


@database_sync_to_async
def get_user_from_token(token):
    try:
        validated_token = JWTAuthentication().get_validated_token(token)
        return JWTAuthentication().get_user(validated_token)
    except Exception:
        logger.warning('WebSocket JWT authentication failed')
        return None


class JWTAuthMiddleware:
    """Authenticate WebSocket clients with ?token=<JWT>."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        token = parse_qs(query_string).get('token', [None])[0]
        scope['user'] = await get_user_from_token(token) if token else None
        return await self.app(scope, receive, send)
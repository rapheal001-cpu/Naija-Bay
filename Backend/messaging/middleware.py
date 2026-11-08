"""Async JWT cookie authentication for WebSocket scopes (SkillStream pattern).

Naija-Bay tokens live in httpOnly cookies set by auth_kit; the access cookie
name comes from ``AUTH_KIT['AUTH_JWT_COOKIE_NAME']`` (default ``access``).
"""

from http.cookies import SimpleCookie

from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from accounts.models import User


@database_sync_to_async
def get_user_for_access_token(token):
    try:
        access_token = AccessToken(token)
        user_id_claim = settings.SIMPLE_JWT.get("USER_ID_CLAIM", "user_id")
        user_id = access_token[user_id_claim]
        return User.objects.get(pk=user_id, is_active=True)
    except (TokenError, KeyError, TypeError, ValueError, User.DoesNotExist):
        return AnonymousUser()


class JWTCookieAuthMiddleware(BaseMiddleware):
    """Authenticates sockets using the JWT cookie set by the REST login."""

    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        headers = dict(scope.get("headers", []))
        raw_cookie = headers.get(b"cookie", b"").decode("latin1")
        cookies = SimpleCookie()
        cookies.load(raw_cookie)
        cookie_name = settings.AUTH_KIT.get("AUTH_JWT_COOKIE_NAME", "access")
        cookie = cookies.get(cookie_name)
        scope["user"] = (
            await get_user_for_access_token(cookie.value)
            if cookie is not None
            else AnonymousUser()
        )
        return await super().__call__(scope, receive, send)


def jwt_cookie_auth_middleware(inner):
    return JWTCookieAuthMiddleware(inner)

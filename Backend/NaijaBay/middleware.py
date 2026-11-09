"""Custom security middleware (SkillStream pattern, adapted to Naija-Bay)."""

import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.urls import reverse
from django.middleware.csrf import get_token

try:
    # Django's own token matcher (handles masked or raw tokens).
    from django.middleware.csrf import _check_token_format, _does_token_match
    from django.middleware.csrf import InvalidTokenFormat

    def _valid_csrf_token(request):
        cookie = request.COOKIES.get("csrftoken", "")
        header = request.META.get("HTTP_X_CSRFTOKEN", "")
        if not cookie or not header:
            return False
        try:
            _check_token_format(header)
            return bool(_does_token_match(header, cookie))
        except (ValueError, TypeError):
            return False
        except Exception:
            return False

except ImportError:
    from django.middleware.csrf import _unmask_cipher_token  # noqa: F401
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)

# Auth cookies issued by DRF Auth Kit (see settings.AUTH_KIT) — their mere
# presence means the request MIGHT be exercised by a browser, so CSRF
# validation applies. Requests without them (Authorization-header API
# clients) cannot be driven by a browser form and are left to auth.
AUTH_COOKIE_NAMES = ("access", "refresh")

# Unsafe /api/ paths CSRF validation must never break:
# - the Paystack webhook authenticates via HMAC signature, not cookies.
CSRF_EXEMPT_PATH_PREFIXES = ("/api/v1/payments/webhook/",)


class CsrfGuardMiddleware:
    """Enforces double-submit CSRF tokens for cookie-authenticated unsafe API calls.

    The JWT auth is cookie-based, so a browser can be tricked into sending a
    forged request (form POST / fetch with cookies). DRF APIViews are
    CSRF-exempt by design, hence this guard. It also issues the
    ``csrftoken`` cookie on every response (via ``get_token``) so the SPA
    can read it and send ``X-CSRFToken`` back. Unauthenticated or
    Authorization-header requests are not browser-exercisable and pass.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Issue/refresh the csrftoken cookie the SPA reads into X-CSRFToken.
        get_token(request)

        if request.method not in SAFE_METHODS and request.path.startswith("/api/"):
            if not request.path.startswith(CSRF_EXEMPT_PATH_PREFIXES):
                if any(name in request.COOKIES for name in AUTH_COOKIE_NAMES):
                    if not _valid_csrf_token(request):
                        logger.warning(
                            "Blocked cookie-authenticated %s to %s without a valid CSRF token",
                            request.method,
                            request.path,
                        )
                        return JsonResponse(
                            {
                                "code": "csrf_failed",
                                "detail": "CSRF verification failed.",
                                "status": 403,
                            },
                            status=403,
                        )
        return self.get_response(request)

VERSION_HEADERS = (
    "Server",
    "X-Powered-By",
    "X-AspNet-Version",
    "X-AspNetMvc-Version",
    "X-Django-Version",
    "X-Generator",
)


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        for header in VERSION_HEADERS:
            response.headers.pop(header, None)
        if "X-Content-Type-Options" not in response:
            response["X-Content-Type-Options"] = "nosniff"
        if "Referrer-Policy" not in response:
            response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if "Permissions-Policy" not in response:
            response["Permissions-Policy"] = (
                "camera=(), microphone=(), geolocation=(), payment=()"
            )
        if "X-Permitted-Cross-Domain-Policies" not in response:
            response["X-Permitted-Cross-Domain-Policies"] = "none"
        return response


SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


def _origin_of(value):
    if not value or value == "null":
        return None
    parts = urlsplit(value.strip())
    if not parts.scheme or not parts.netloc:
        return None
    return f"{parts.scheme}://{parts.netloc}".lower()


class TrustedOriginMiddleware:
    """Rejects unsafe-method /api/ calls from untrusted cross-site origins."""

    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def _trusted_origins(request):
        trusted = {_origin_of(f"{request.scheme}://{request.get_host()}")}
        for value in (
            list(getattr(settings, "CORS_ALLOWED_ORIGINS", []))
            + list(getattr(settings, "CSRF_TRUSTED_ORIGINS", []))
            + [getattr(settings, "FRONTEND_URL", "")]
        ):
            trusted.add(_origin_of(value))
        trusted.discard(None)
        return trusted

    def __call__(self, request):
        if request.method not in SAFE_METHODS and request.path.startswith("/api/"):
            header_origin = request.META.get("HTTP_ORIGIN")
            referer = request.META.get("HTTP_REFERER")
            if header_origin is not None:
                source = _origin_of(header_origin)
                present = True
            elif referer:
                source = _origin_of(referer)
                present = True
            else:
                source = None
                present = False

                # Approved Option A: browser cookie-authenticated unsafe
                # requests must arrive with an Origin or Referer (browsers
                # always send one; a request without either is suspicious).
                # Token-less non-cookie API clients are untouched here.
                if any(name in request.COOKIES for name in AUTH_COOKIE_NAMES):
                    logger.warning(
                        "Blocked cookie-authenticated %s to %s without Origin/Referer",
                        request.method,
                        request.path,
                    )
                    return JsonResponse(
                        {
                            "code": "missing_origin",
                            "detail": "Origin or Referer header required.",
                            "status": 403,
                        },
                        status=403,
                    )

            if present and source not in self._trusted_origins(request):
                logger.warning(
                    "Blocked cross-site %s to %s from origin %r",
                    request.method,
                    request.path,
                    header_origin or referer,
                )
                return JsonResponse(
                    {
                        "code": "untrusted_origin",
                        "detail": "This request came from an untrusted origin.",
                        "status": 403,
                    },
                    status=403,
                )
        return self.get_response(request)


class OwnerOnlyDjangoAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            admin_path = reverse("admin:index")
        except Exception:
            admin_path = "/admin/"
        if request.path.startswith(admin_path):
            user = getattr(request, "user", None)
            if user is None or not user.is_authenticated or not user.is_superuser:
                raise PermissionDenied
        return self.get_response(request)

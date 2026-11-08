"""Custom security middleware (SkillStream pattern, adapted to Naija-Bay)."""

import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.urls import reverse
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)

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

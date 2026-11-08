"""Read-through caching for Naija-Bay (SkillStream pattern).

Generation-based invalidation: every namespace has a generation UUID; bumping
it (``invalidate_read_cache``) orphans all keys derived from the old
generation. Keys incorporate the user id so personalized responses stay
private, plus path/media/language for correct shared caching.

Cache failures degrade to a miss, never an exception (same as SkillStream).
"""

import hashlib
import json
import logging
from functools import wraps
from uuid import uuid4

from django.core.cache import cache
from django.db import transaction
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

logger = logging.getLogger(__name__)

# Namespaces used across Naija-Bay.
ATTRIBUTE_DEFINITIONS_CACHE = "products:attribute-definitions"
CATEGORY_LIST_CACHE = "products:categories"
PRODUCT_LIST_CACHE = "products:list"
PRODUCT_DETAIL_CACHE = "products:detail"
READ_CACHE_TIMEOUT = 30 * 60  # 30 minutes
_CACHE_MISS = object()


def _cache_get(key, default=None):
    try:
        return cache.get(key, default)
    except Exception:
        logger.warning("Cache get failed for key=%s; treating as a miss", key, exc_info=True)
        return default


def _cache_set(key, value, timeout):
    try:
        cache.set(key, value, timeout=timeout)
        return True
    except Exception:
        logger.warning("Cache set failed for key=%s; skipping", key, exc_info=True)
        return False


def _generation_key(namespace):
    return f"api-read-cache:{namespace}:generation"


def invalidate_read_cache(namespace):
    cache.set(_generation_key(namespace), uuid4().hex, timeout=None)


def _invalidate_read_cache_safely(namespace):
    try:
        invalidate_read_cache(namespace)
    except Exception:
        logger.error(
            "Read-cache invalidation failed for namespace=%s; cached lists may be stale until they expire",
            namespace,
            exc_info=True,
        )


def schedule_read_cache_invalidation(namespace):
    transaction.on_commit(
        lambda: _invalidate_read_cache_safely(namespace), robust=True
    )


def read_cache_key(namespace, request):
    generation = _cache_get(_generation_key(namespace), "initial")
    user = getattr(request, "user", None)
    user_id = (
        str(user.pk)
        if user is not None and getattr(user, "is_authenticated", False)
        else "anonymous"
    )
    media_type = getattr(request, "accepted_media_type", None) or request.headers.get(
        "Accept", ""
    )
    language = request.headers.get("Accept-Language", "")
    material = "\0".join(
        (
            str(generation),
            user_id,
            request.get_full_path(),
            media_type,
            language,
        )
    )
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
    return f"api-read-cache:{namespace}:{digest}"


def cached_read_list(namespace, timeout=READ_CACHE_TIMEOUT):
    """Decorator: cache 200 GET responses per (namespace, user, path)."""

    def decorate(method):
        @wraps(method)
        def wrapped(view, request, *args, **kwargs):
            if request.method != "GET":
                return method(view, request, *args, **kwargs)

            key = read_cache_key(namespace, request)
            cached = _cache_get(key, _CACHE_MISS)
            if cached is not _CACHE_MISS:
                response = Response(cached["data"], status=cached["status"])
                for header, value in cached["headers"].items():
                    response[header] = value
                return response

            response = method(view, request, *args, **kwargs)
            if response.status_code == 200 and hasattr(response, "data"):
                data = json.loads(JSONRenderer().render(response.data))
                _cache_set(
                    key,
                    {
                        "data": data,
                        "status": response.status_code,
                        "headers": dict(response.items()),
                    },
                    timeout,
                )
            return response

        return wrapped

    return decorate

"""Media storage, upload purposes and validation (SkillStream pattern).

Central source of truth for:
- upload purposes and their key prefixes
- storage backend detection (local / cloudinary / s3)
- validation and basic storage helpers
"""

from __future__ import annotations

import logging
from typing import Any

try:
    import boto3
except ImportError:  # optional in development; required only for S3 storage
    boto3 = None

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)



UPLOAD_PURPOSES = {
    "product-image": {"prefix": "products/images", "kind": "image"},
    "ad-video": {"prefix": "products/videos", "kind": "video"},
    "store-logo": {"prefix": "stores/logos", "kind": "image"},
    "store-banner": {"prefix": "stores/banners", "kind": "image"},
    "user-avatar": {"prefix": "accounts/avatars", "kind": "image"},
    "chat-image": {"prefix": "messaging/images", "kind": "image"},
    "chat-audio": {"prefix": "messaging/audio", "kind": "video"},
    "verification-selfie": {"prefix": "verification/selfies", "kind": "image"},
    "verification-document": {"prefix": "verification/documents", "kind": "image"},
}

IMAGE_PURPOSES = frozenset(
    name for name, spec in UPLOAD_PURPOSES.items() if spec["kind"] == "image"
)
VIDEO_PURPOSES = frozenset(
    name for name, spec in UPLOAD_PURPOSES.items() if spec["kind"] == "video"
)

IMAGE_CONTENT_TYPES = frozenset({"image/jpeg", "image/jpg", "image/png"})
VIDEO_CONTENT_TYPES = frozenset(
    {"video/mp4", "video/webm", "video/quicktime", "video/x-matroska", "audio/webm", "audio/mp4", "audio/mpeg"}
)
IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png"})
VIDEO_EXTENSIONS = frozenset({".mp4", ".webm", ".mov", ".mkv", ".m4a", ".mp3"})

MAX_IMAGE_SIZE = 2 * 1024 * 1024        # 2 MB — matches product image limits
MAX_VIDEO_SIZE = 100 * 1024 * 1024      # 100 MB — marketplace ad videos / voice notes



def get_media_storage():
    return default_storage


def storage_backend_name() -> str:
    return str(getattr(settings, "MEDIA_STORAGE_BACKEND", "local")).lower()


def cloudinary_configured() -> bool:
    cfg = getattr(settings, "CLOUDINARY_STORAGE", None) or {}
    return storage_backend_name() == "cloudinary" and all(
        cfg.get(key) for key in ("CLOUD_NAME", "API_KEY", "API_SECRET")
    )


def cloudinary_credentials() -> tuple[str, str, str]:
    cfg = getattr(settings, "CLOUDINARY_STORAGE", None) or {}
    return (
        str(cfg.get("CLOUD_NAME", "")),
        str(cfg.get("API_KEY", "")),
        str(cfg.get("API_SECRET", "")),
    )


def s3_configured() -> bool:
    return storage_backend_name() == "s3" and bool(
        getattr(settings, "AWS_STORAGE_BUCKET_NAME", "")
    )


def get_s3_client():
    if boto3 is None:
        raise RuntimeError("boto3 is required for S3 media storage.")
    kwargs: dict[str, Any] = {
        "region_name": getattr(settings, "AWS_S3_REGION_NAME", None),
    }
    if getattr(settings, "AWS_S3_ENDPOINT_URL", ""):
        kwargs["endpoint_url"] = settings.AWS_S3_ENDPOINT_URL
    if getattr(settings, "AWS_ACCESS_KEY_ID", ""):
        kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
    if getattr(settings, "AWS_SECRET_ACCESS_KEY", ""):
        kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
    return boto3.client("s3", **kwargs)


def cloudinary_prefix() -> str:
    if not cloudinary_configured():
        return ""
    try:
        from cloudinary_storage import app_settings
        return str(getattr(app_settings, "PREFIX", "")).strip("/")
    except Exception:
        return ""



def media_exists(name: str) -> bool:
    return bool(name) and get_media_storage().exists(name)


def open_media(name: str):
    return get_media_storage().open(name, "rb")


def media_url(name: str) -> str:
    return get_media_storage().url(name)


def save_media_bytes(name: str, payload: bytes, *, restore: bytes | None = None) -> str:
    storage = get_media_storage()
    existed = storage.exists(name)
    if existed:
        storage.delete(name)
    try:
        return storage.save(name, ContentFile(payload))
    except Exception:
        if existed and restore is not None:
            try:
                storage.save(name, ContentFile(restore))
            except Exception:
                pass
        raise


def delete_media(name: str) -> None:
    if not name:
        return
    storage = get_media_storage()
    try:
        if storage.exists(name):
            storage.delete(name)
    except Exception:
        logger.exception("Could not delete media %s", name)


def read_media_bytes(name: str) -> bytes:
    with open_media(name) as handle:
        return handle.read()



def validate_image_upload(value, *, label: str = "Image", max_size: int | None = None):
    if value is None or isinstance(value, str):
        return value
    limit = max_size or MAX_IMAGE_SIZE
    if getattr(value, "size", 0) > limit:
        raise ValueError(f"{label} must be {limit // (1024 * 1024)}MB or smaller.")
    if not str(getattr(value, "name", "")).lower().endswith(tuple(IMAGE_EXTENSIONS)):
        raise ValueError(f"{label} format is not supported.")
    content_type = str(getattr(value, "content_type", "") or "").lower()
    if content_type and content_type not in IMAGE_CONTENT_TYPES:
        raise ValueError(f"{label} format is not supported.")
    try:
        if hasattr(value, "seek"):
            value.seek(0)
        Image.open(value).verify()
    except (UnidentifiedImageError, OSError, ValueError):
        raise ValueError(f"{label} is not a valid image.")
    finally:
        if hasattr(value, "seek"):
            value.seek(0)
    return value


def validate_video_upload(value, *, label: str = "Video"):
    if value is None or isinstance(value, str):
        return value
    if not str(getattr(value, "name", "")).lower().endswith(tuple(VIDEO_EXTENSIONS)):
        raise ValueError(f"{label} format is not supported.")
    if getattr(value, "size", 0) > MAX_VIDEO_SIZE:
        raise ValueError(f"{label} is too large (max 100MB).")
    return value

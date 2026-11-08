"""Direct-to-storage image uploads (SkillStream pattern, Naija-Bay scoped).

Images are at most a few megabytes here, so S3 "post" (presigned POST) is
enough; multipart resumability is unnecessary complexity for 2 MB images.

Flow:
1. ``POST /api/v1/core/media/upload-initiate`` returns ``{mode, key, ...}``.
2. The browser uploads straight to Cloudinary (signed params) / S3 (presigned
   POST), or falls back to multipart through Django (``mode: local``).
3. The client attaches the returned ``key`` when creating product images via
   ``POST /api/v1/products/create/images/`` with ``{"product": id, "key": k}``.
"""

import hashlib
import logging
import time
import uuid
from pathlib import Path

from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

IMAGE_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png"}
VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # mirrors ProductImageSerializer (2 MB)
IMAGE_FORMATS = "jpg,jpeg,png"

PURPOSE_PREFIX = "naijabay"


def _cloudinary_credentials():
    name = getattr(settings, "CLOUDINARY_STORAGE", {}).get("CLOUD_NAME", "")
    key = getattr(settings, "CLOUDINARY_STORAGE", {}).get("API_KEY", "")
    secret = getattr(settings, "CLOUDINARY_STORAGE", {}).get("API_SECRET", "")
    if name and key and secret:
        return name, key, secret
    return None, None, None


def _key(user_id, filename):
    suffix = Path(filename or "upload").suffix.lower()
    if suffix not in VALID_IMAGE_EXTENSIONS:
        suffix = ".jpg"
    return f"{PURPOSE_PREFIX}/{user_id}/{uuid.uuid4().hex}{suffix}"


def is_own_direct_upload_key(key, user_id):
    """Keys are ``naijabay/<user_id>/<uuid><ext>`` — ownership is structural."""
    value = str(key or "").strip()
    if not value or ".." in value or value.startswith(("/", "\\")) or user_id is None:
        return False
    return value.startswith(f"{PURPOSE_PREFIX}/{user_id}/")


class UploadInitiateSerializer(serializers.Serializer):
    filename = serializers.CharField(required=False, allow_blank=True, max_length=255)
    content_type = serializers.CharField(max_length=100)
    size = serializers.IntegerField(min_value=1)
    purpose = serializers.CharField(required=False, default="product_image")


def _cloudinary_signature(params, api_secret):
    payload = "&".join(f"{k}={params[k]}" for k in sorted(params))
    return hashlib.sha1(f"{payload}{api_secret}".encode("utf-8")).hexdigest()


class UploadInitiateView(APIView):
    """Issues signed direct-to-storage upload instructions (images only)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UploadInitiateSerializer,
        responses={
            200: None,
            400: None,
        },
    )
    def post(self, request):
        serializer = UploadInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content_type = serializer.validated_data["content_type"].lower()
        size = serializer.validated_data["size"]
        filename = serializer.validated_data.get("filename") or ""

        if content_type not in IMAGE_CONTENT_TYPES:
            return Response({"detail": "Unsupported image type. Use JPG, JPEG or PNG."}, status=status.HTTP_400_BAD_REQUEST)
        if size > MAX_IMAGE_SIZE:
            return Response({"detail": "The selected image exceeds the 2 MB limit."}, status=status.HTTP_400_BAD_REQUEST)

        key = _key(request.user.pk, filename)
        cloud_name, api_key, api_secret = _cloudinary_credentials()

        if getattr(settings, "MEDIA_STORAGE_BACKEND", "local") == "cloudinary" and cloud_name:
            timestamp = int(time.time())
            params = {
                "public_id": key,
                "tags": "naijabay",
                "timestamp": timestamp,
                "allowed_formats": IMAGE_FORMATS,
            }
            return Response({
                "mode": "cloudinary",
                "key": key,
                "url": f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload",
                "fields": {
                    "api_key": api_key,
                    "timestamp": str(timestamp),
                    "signature": _cloudinary_signature(params, api_secret),
                    "public_id": key,
                    "tags": "naijabay",
                    "allowed_formats": IMAGE_FORMATS,
                },
                "max_file_size": MAX_IMAGE_SIZE,
            })

        if getattr(settings, "MEDIA_STORAGE_BACKEND", "local") == "s3" and settings.AWS_STORAGE_BUCKET_NAME:
            import boto3  # late import; dev installs skip it

            client = boto3.client(
                "s3",
                region_name=settings.AWS_S3_REGION_NAME,
                **({"endpoint_url": settings.AWS_S3_ENDPOINT_URL} if settings.AWS_S3_ENDPOINT_URL else {}),
            )
            post = client.generate_presigned_post(
                settings.AWS_STORAGE_BUCKET_NAME,
                key,
                Fields={"Content-Type": content_type},
                Conditions=[
                    ["content-length-range", 1, size],
                    {"Content-Type": content_type},
                ],
                ExpiresIn=900,
            )
            return Response({
                "mode": "s3",
                "strategy": "post",
                "key": key,
                "upload": post,
                "max_file_size": MAX_IMAGE_SIZE,
            })

        # Local storage: upload through the app server (multipart fallback).
        return Response({
            "mode": "local",
            "detail": "Local storage: the file will be sent through the app server.",
            "max_file_size": MAX_IMAGE_SIZE,
        })


upload_initiate_view = UploadInitiateView.as_view()

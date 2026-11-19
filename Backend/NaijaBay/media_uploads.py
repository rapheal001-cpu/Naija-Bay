"""Direct-to-storage media uploads (SkillStream pattern, Naija-Bay scoped).

Flow:
1. ``POST /api/v1/storage/media/uploads/initiate/`` with
   ``{purpose, filename, content_type, size}`` returns ``{mode, key, ...}``.
2. The browser uploads straight to Cloudinary (signed params) or S3
   (presigned POST / multipart), or falls back to multipart through Django
   (``mode: local``).
3. The client attaches the returned ``key`` to the domain create/update
   endpoint. Serializers validate ownership with ``is_own_direct_upload_key``.

S3 multipart uploads are resumable: ``parts``/``part-url``/``complete``/``abort``.
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from pathlib import Path

try:
    from botocore.exceptions import ClientError
except ImportError:  # boto3/botocore are optional in development
    class ClientError(Exception):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
            self.response = {}

from django.conf import settings
from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .direct_uploads import is_own_direct_upload_key  # re-exported for older imports
from .media import (
    IMAGE_CONTENT_TYPES,
    IMAGE_EXTENSIONS,
    IMAGE_PURPOSES,
    MAX_IMAGE_SIZE,
    MAX_VIDEO_SIZE,
    UPLOAD_PURPOSES,
    VIDEO_CONTENT_TYPES,
    VIDEO_EXTENSIONS,
    cloudinary_configured,
    cloudinary_credentials,
    cloudinary_prefix,
    get_s3_client,
    s3_configured,
)

logger = logging.getLogger(__name__)

PART_SIZE = 10 * 1024 * 1024
PURPOSE_PREFIXES = {name: spec["prefix"] for name, spec in UPLOAD_PURPOSES.items()}
IMAGE_FORMATS = "jpg,jpeg,png"
VIDEO_FORMATS = "mp4,webm,mov,mkv"



class UploadErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()


class ResumeUploadSerializer(serializers.Serializer):
    key = serializers.CharField()
    upload_id = serializers.CharField(max_length=256)


class UploadInitiateSerializer(serializers.Serializer):
    purpose = serializers.ChoiceField(
        choices=list(PURPOSE_PREFIXES), required=False, default="product-image"
    )
    content_type = serializers.CharField(max_length=100)
    size = serializers.IntegerField(min_value=1)
    filename = serializers.CharField(required=False, allow_blank=True, max_length=255)
    resume = ResumeUploadSerializer(required=False)


class PresignedPostSerializer(serializers.Serializer):
    url = serializers.URLField()
    fields = serializers.DictField(child=serializers.CharField())


class UploadInitiateS3ResponseSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=["s3"])
    strategy = serializers.ChoiceField(choices=["post", "multipart"])
    key = serializers.CharField()
    max_file_size = serializers.IntegerField()
    upload = PresignedPostSerializer(required=False)
    upload_id = serializers.CharField(required=False)
    part_size = serializers.IntegerField(required=False)


class UploadInitiateLocalResponseSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=["local"])
    detail = serializers.CharField(required=False)
    max_file_size = serializers.IntegerField()


class UploadInitiateCloudinaryResponseSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=["cloudinary"])
    key = serializers.CharField()
    resource_type = serializers.ChoiceField(choices=["raw", "image"])
    url = serializers.URLField()
    fields = serializers.DictField(child=serializers.CharField())
    max_file_size = serializers.IntegerField()


UploadInitiateResponseSerializer = PolymorphicProxySerializer(
    component_name="UploadInitiateResponse",
    serializers=[
        UploadInitiateS3ResponseSerializer,
        UploadInitiateCloudinaryResponseSerializer,
        UploadInitiateLocalResponseSerializer,
    ],
    resource_type_field_name="mode",
)


class UploadPartUrlSerializer(serializers.Serializer):
    key = serializers.CharField()
    upload_id = serializers.CharField()
    part_number = serializers.IntegerField(min_value=1, max_value=10000)


class UploadPartSerializer(serializers.Serializer):
    PartNumber = serializers.IntegerField(min_value=1, max_value=10000)
    ETag = serializers.CharField()


class UploadCompleteSerializer(serializers.Serializer):
    key = serializers.CharField()
    upload_id = serializers.CharField()
    parts = UploadPartSerializer(many=True, allow_empty=False)



def _int_or_error(value, field):
    try:
        return int(value), None
    except (TypeError, ValueError):
        return None, Response({"detail": f"Invalid {field}."}, status=400)


def _validate(request):
    serializer = UploadInitiateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    purpose = serializer.validated_data["purpose"]
    content_type = str(serializer.validated_data["content_type"]).lower()
    size = serializer.validated_data["size"]

    is_image = purpose in IMAGE_PURPOSES
    allowed = IMAGE_CONTENT_TYPES if is_image else VIDEO_CONTENT_TYPES
    limit = MAX_IMAGE_SIZE if is_image else MAX_VIDEO_SIZE
    if content_type not in allowed:
        return None, Response({"detail": "Unsupported media type."}, status=400)
    if size <= 0 or size > limit:
        return None, Response(
            {"detail": "The selected file exceeds the allowed upload size."}, status=400
        )
    return (purpose, content_type, size, serializer.validated_data.get("filename", "")), None


def _key(user_id, purpose, filename):
    suffix = Path(filename or "upload").suffix.lower()
    allowed = IMAGE_EXTENSIONS if purpose in IMAGE_PURPOSES else VIDEO_EXTENSIONS
    if suffix not in allowed:
        suffix = ".jpg" if purpose in IMAGE_PURPOSES else ".mp4"
    prefix = PURPOSE_PREFIXES[purpose]
    cloud = cloudinary_prefix()
    if cloud:
        prefix = f"{cloud}/{prefix}"
    return f"{prefix}/{user_id}/{uuid.uuid4().hex}{suffix}"


def _key_matches_purpose(key, purpose) -> bool:
    prefix = PURPOSE_PREFIXES.get(purpose)
    if not prefix:
        return False
    candidates = [prefix]
    cloud = cloudinary_prefix()
    if cloud:
        candidates.append(f"{cloud}/{prefix}")
    value = str(key)
    if ".." in value.split("/") or value.startswith(("/", "\\")):
        return False
    return any(value.startswith(f"{candidate}/") for candidate in candidates)


def _owns_key(user_id, key) -> bool:
    return is_own_direct_upload_key(key, user_id)


def _cloudinary_signature(params, api_secret):
    payload = "&".join(f"{k}={params[k]}" for k in sorted(params))
    return hashlib.sha1(f"{payload}{api_secret}".encode("utf-8")).hexdigest()


def _check_owned(request, key, upload_id=None):
    value = str(key or "").strip()
    if (
        not value
        or ".." in value.split("/")
        or value.startswith(("/", "\\"))
        or not _owns_key(request.user.pk, value)
    ):
        return False
    if upload_id is not None and (
        not upload_id or len(str(upload_id)) > 256 or any(ch.isspace() for ch in str(upload_id))
    ):
        return False
    return True



class UploadInitiateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UploadInitiateSerializer,
        responses={200: UploadInitiateResponseSerializer, 400: UploadErrorSerializer},
    )
    def post(self, request):
        values, error = _validate(request)
        if error:
            return error
        purpose, content_type, size, filename = values

        resume = request.data.get("resume")
        if resume is not None:
            return self._resume_response(request, purpose, size, resume)

        if cloudinary_configured():
            return self._cloudinary_response(request, purpose, content_type, size)

        if not s3_configured():
            return Response({
                "mode": "local",
                "detail": "Local storage: the file will be sent through the app server.",
                "max_file_size": MAX_VIDEO_SIZE,
            })

        key = _key(request.user.pk, purpose, filename)
        client = get_s3_client()
        multipart = size >= PART_SIZE or content_type.startswith("video/")
        if not multipart:
            post = client.generate_presigned_post(
                settings.AWS_STORAGE_BUCKET_NAME,
                key,
                Fields={"Content-Type": content_type},
                Conditions=[["content-length-range", 1, size], {"Content-Type": content_type}],
                ExpiresIn=900,
            )
            return Response({
                "mode": "s3", "strategy": "post", "key": key,
                "upload": post, "max_file_size": size,
            })

        upload = client.create_multipart_upload(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key, ContentType=content_type
        )
        return Response({
            "mode": "s3", "strategy": "multipart", "key": key,
            "upload_id": upload["UploadId"], "part_size": PART_SIZE,
            "max_file_size": size,
        })

    def _resume_response(self, request, purpose, size, resume):
        if not s3_configured():
            return Response(
                {"code": "resume_not_supported", "detail": "Resume is only supported for S3 storage."},
                status=400,
            )
        if not isinstance(resume, dict):
            return Response({"detail": "Invalid resume payload."}, status=400)
        key = str(resume.get("key", "")).strip()
        upload_id = str(resume.get("upload_id", "")).strip()
        if (
            not key or not upload_id
            or not _check_owned(request, key, upload_id)
            or not _key_matches_purpose(key, purpose)
        ):
            return Response({"detail": "Invalid resume payload."}, status=400)
        try:
            get_s3_client().list_parts(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key, UploadId=upload_id
            )
        except ClientError as exc:
            code = str((exc.response or {}).get("Error", {}).get("Code", ""))
            if code == "NoSuchUpload":
                return Response(
                    {"code": "upload_session_not_found", "detail": "Upload session not found; start again."},
                    status=400,
                )
            logger.exception("S3 list_parts failed for %s", key)
            return Response({"detail": "Could not reach storage; please try again."}, status=502)
        except Exception:
            logger.exception("S3 list_parts failed for %s", key)
            return Response({"detail": "Could not reach storage; please try again."}, status=502)
        return Response({
            "mode": "s3", "strategy": "multipart", "key": key,
            "upload_id": upload_id, "part_size": PART_SIZE, "max_file_size": size,
        })

    def _cloudinary_response(self, request, purpose, content_type, size):
        cloud_name, api_key, api_secret = cloudinary_credentials()
        is_image = purpose in IMAGE_PURPOSES
        resource_type = "image" if is_image else "raw"
        key = _key(request.user.pk, purpose, request.data.get("filename", ""))
        timestamp = int(time.time())
        params = {
            "public_id": key,
            "tags": "naijabay",
            "timestamp": timestamp,
            "allowed_formats": IMAGE_FORMATS if is_image else VIDEO_FORMATS,
        }
        preset = getattr(settings, "CLOUDINARY_UPLOAD_PRESET", "")
        if preset:
            params["upload_preset"] = preset
        return Response({
            "mode": "cloudinary",
            "key": key,
            "resource_type": resource_type,
            "url": f"https://api.cloudinary.com/v1_1/{cloud_name}/{resource_type}/upload",
            "fields": {
                "api_key": api_key,
                "timestamp": str(timestamp),
                "signature": _cloudinary_signature(params, api_secret),
                "public_id": key,
                "tags": params["tags"],
                "allowed_formats": params["allowed_formats"],
                **({"upload_preset": preset} if preset else {}),
            },
            "max_file_size": size,
        })


upload_initiate_view = UploadInitiateView.as_view()


class UploadPartsListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not s3_configured():
            return Response({"detail": "Resume is only supported for S3 storage."}, status=503)
        key = str(request.data.get("key", "")).strip()
        upload_id = str(request.data.get("upload_id", "")).strip()
        if not _check_owned(request, key, upload_id):
            return Response({"detail": "Invalid request."}, status=400)
        try:
            response = get_s3_client().list_parts(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key, UploadId=upload_id
            )
        except ClientError as exc:
            code = str((exc.response or {}).get("Error", {}).get("Code", ""))
            if code == "NoSuchUpload":
                return Response(
                    {"code": "upload_session_not_found", "detail": "Upload session not found; start again."},
                    status=400,
                )
            return Response({"detail": "Could not reach storage; please try again."}, status=502)
        except Exception:
            return Response({"detail": "Could not reach storage; please try again."}, status=502)
        parts = [
            {"PartNumber": int(p["PartNumber"]), "ETag": str(p["ETag"]), "Size": int(p.get("Size", 0))}
            for p in response.get("Parts", [])
        ]
        return Response({"parts": parts})


upload_parts_list_view = UploadPartsListView.as_view()


class UploadPartUrlView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not s3_configured():
            return Response({"detail": "S3 direct uploads are not configured."}, status=503)
        key = str(request.data.get("key", "")).strip()
        upload_id = str(request.data.get("upload_id", "")).strip()
        part_number, err = _int_or_error(request.data.get("part_number", 0) or 0, "part_number")
        if err:
            return err
        if not _check_owned(request, key, upload_id) or not 1 <= part_number <= 10000:
            return Response({"detail": "Invalid multipart upload data."}, status=400)
        try:
            url = get_s3_client().generate_presigned_url(
                "upload_part",
                Params={
                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "Key": key, "UploadId": upload_id, "PartNumber": part_number,
                },
                ExpiresIn=900,
            )
        except Exception:
            logger.exception("S3 generate_presigned_url failed for %s", key)
            return Response({"detail": "Could not reach storage; please try again."}, status=502)
        return Response({"url": url})


upload_part_url_view = UploadPartUrlView.as_view()


class UploadCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not s3_configured():
            return Response({"detail": "S3 direct uploads are not configured."}, status=503)
        key = str(request.data.get("key", ""))
        upload_id = str(request.data.get("upload_id", ""))
        parts = request.data.get("parts", [])
        if not _check_owned(request, key, upload_id) or not isinstance(parts, list) or not parts:
            return Response({"detail": "Multipart parts are required."}, status=400)
        completed = []
        for part in parts:
            if not isinstance(part, dict) or "PartNumber" not in part or "ETag" not in part:
                return Response({"detail": "Multipart parts are required."}, status=400)
            number, err = _int_or_error(part["PartNumber"], "part_number")
            if err or not 1 <= number <= 10000 or not str(part.get("ETag", "")).strip():
                return Response({"detail": "Multipart parts are required."}, status=400)
            completed.append({"PartNumber": number, "ETag": str(part["ETag"])})
        try:
            get_s3_client().complete_multipart_upload(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=key, UploadId=upload_id,
                MultipartUpload={"Parts": completed},
            )
        except ClientError as exc:
            code = str((exc.response or {}).get("Error", {}).get("Code", ""))
            if code in ("NoSuchUpload", "InvalidPart"):
                return Response({"detail": "Upload session not found; start again."}, status=400)
            return Response({"detail": "Could not reach storage; please try again."}, status=502)
        except Exception:
            return Response({"detail": "Could not reach storage; please try again."}, status=502)
        return Response({"key": key, "status": "uploaded"}, status=status.HTTP_201_CREATED)


upload_complete_view = UploadCompleteView.as_view()


class UploadAbortView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        key = str(request.data.get("key", "")).strip()
        upload_id = str(request.data.get("upload_id", "")).strip()
        if s3_configured() and key and _check_owned(request, key, upload_id):
            try:
                get_s3_client().abort_multipart_upload(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key, UploadId=upload_id
                )
            except ClientError as exc:
                code = str((exc.response or {}).get("Error", {}).get("Code", ""))
                if code != "NoSuchUpload":
                    return Response({"detail": "Could not reach storage; please try again."}, status=502)
            except Exception:
                return Response({"detail": "Could not reach storage; please try again."}, status=502)
        return Response(status=status.HTTP_204_NO_CONTENT)


upload_abort_view = UploadAbortView.as_view()

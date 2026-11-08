"""Custom media storage backends (SkillStream pattern).

Selectable per environment via ``MEDIA_STORAGE_BACKEND``:

* development: ``local`` (filesystem, default) or ``cloudinary``
* production:  ``s3`` (AWS/R2-compatible via custom endpoint) or ``cloudinary``
"""

import os

from cloudinary_storage.storage import RESOURCE_TYPES, MediaCloudinaryStorage


class AutoResourceCloudinaryStorage(MediaCloudinaryStorage):
    """Stores media on Cloudinary with automatic resource-type detection."""

    RESOURCE_TYPE = RESOURCE_TYPES["IMAGE"]

    def _get_resource_type(self, name):
        extension = os.path.splitext(str(name).split("?", 1)[0])[1].lower()
        if extension in {".mp4", ".webm", ".mov", ".mkv", ".avi", ".m4v"}:
            return RESOURCE_TYPES["VIDEO"]
        if extension in {".pdf", ".zip", ".doc", ".docx", ".xls", ".xlsx", ".txt"}:
            return RESOURCE_TYPES["RAW"]
        return RESOURCE_TYPES["IMAGE"]


class S3MediaStorage:
    """S3 (or R2-compatible) media storage — lazy boto3 import keeps dev light."""

    def __init__(self, *args, **kwargs):
        from django.conf import settings

        self.bucket = settings.AWS_STORAGE_BUCKET_NAME
        self.region = settings.AWS_S3_REGION_NAME
        self.endpoint = settings.AWS_S3_ENDPOINT_URL
        self.location = "media"

    def _client(self):
        import boto3

        kwargs = {"region_name": self.region}
        if self.endpoint:
            kwargs["endpoint_url"] = self.endpoint
        return boto3.client("s3", **kwargs)

    def _save(self, name, content):
        content.seek(0)
        self._client().upload_fileobj(content, self.bucket, f"media/{name}")
        return name

    def _open(self, name, mode="rb"):
        from django.core.files import File

        obj = self._client().get_object(Bucket=self.bucket, Key=f"media/{name}")
        return File(obj["Body"])

    def exists(self, name):
        from botocore.exceptions import ClientError

        try:
            self._client().head_object(Bucket=self.bucket, Key=f"media/{name}")
            return True
        except ClientError:
            return False

    def delete(self, name):
        self._client().delete_object(Bucket=self.bucket, Key=f"media/{name}")

    def url(self, name):
        from django.conf import settings

        if settings.AWS_S3_CUSTOM_DOMAIN:
            return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/media/{name}"
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/media/{name}"

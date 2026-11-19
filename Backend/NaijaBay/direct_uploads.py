"""Support for object keys produced by direct-to-storage uploads.

Ported from the SkillStream pattern: a key is trusted only if it carries the
caller's user id under a known purpose prefix and contains no traversal.
"""

from rest_framework import serializers

from .media import UPLOAD_PURPOSES, cloudinary_prefix


def _prefixes(purpose=None) -> list[str]:
    if purpose is None:
        base = {spec["prefix"] for spec in UPLOAD_PURPOSES.values()}
    else:
        purposes = [purpose] if isinstance(purpose, str) else list(purpose)
        base = set()
        for item in purposes:
            spec = UPLOAD_PURPOSES.get(item)
            if spec is None:
                raise ValueError(f"Unknown upload purpose: {item}")
            base.add(spec["prefix"])
    cloud = cloudinary_prefix()
    prefixes = set(base)
    if cloud:
        prefixes |= {f"{cloud}/{item}" for item in base}
    return sorted(prefixes, key=len, reverse=True)


def is_own_direct_upload_key(key, user_id, *, purpose=None) -> bool:
    value = str(key or "").strip()
    if not value or ".." in value or value.startswith(("/", "\\")) or user_id is None:
        return False
    user = str(user_id)
    return any(
        value.startswith(f"{prefix}/{user}/")
        for prefix in _prefixes(purpose)
    )


def ensure_own_direct_upload_key(value, context, *, purpose=None) -> str:
    key = str(value or "").strip()
    request = context.get("request") if context else None
    user_id = getattr(getattr(request, "user", None), "pk", None)
    if not is_own_direct_upload_key(key, user_id, purpose=purpose):
        raise serializers.ValidationError("This file was not uploaded by you.")
    return key


class ObjectKeyFileField(serializers.FileField):
    """Accepts either an uploaded File or a validated direct-upload object key."""

    def to_internal_value(self, data):
        if isinstance(data, str):
            value = data.strip()
            if not value:
                self.fail("empty")
            return value
        return super().to_internal_value(data)


class ObjectKeyImageField(serializers.ImageField):
    """Accepts either an uploaded Image or a validated direct-upload object key."""

    def to_internal_value(self, data):
        if isinstance(data, str):
            value = data.strip()
            if not value:
                self.fail("empty")
            return value
        return super().to_internal_value(data)

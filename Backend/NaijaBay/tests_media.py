"""Tests for the SkillStream-style media upload API."""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from NaijaBay.direct_uploads import is_own_direct_upload_key


class MediaUploadsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="media@test.local", username="mediauser", password="TestPass123!"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("media-upload-initiate")

    def test_initiate_image_local_mode(self):
        response = self.client.post(self.url, {
            "purpose": "product-image",
            "filename": "photo.jpg",
            "content_type": "image/jpeg",
            "size": 1024,
        }, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["mode"], "local")

    def test_initiate_video_purpose(self):
        response = self.client.post(self.url, {
            "purpose": "ad-video",
            "filename": "clip.mp4",
            "content_type": "video/mp4",
            "size": 5 * 1024 * 1024,
        }, format="json")
        self.assertEqual(response.status_code, 200, response.data)

    def test_invalid_purpose_rejected(self):
        response = self.client.post(self.url, {
            "purpose": "unknown-purpose",
            "content_type": "image/jpeg",
            "size": 1024,
        }, format="json")
        self.assertEqual(response.status_code, 400)

    def test_wrong_content_type_for_purpose(self):
        response = self.client.post(self.url, {
            "purpose": "product-image",
            "content_type": "video/mp4",
            "size": 1024,
        }, format="json")
        self.assertEqual(response.status_code, 400)

    def test_legacy_endpoint_still_works(self):
        response = self.client.post("/api/v1/core/media/upload-initiate/", {
            "filename": "photo.png",
            "content_type": "image/png",
            "size": 512,
        }, format="json")
        self.assertEqual(response.status_code, 200, response.data)

    def test_key_ownership(self):
        key = f"products/images/{self.user.pk}/abc123.jpg"
        self.assertTrue(is_own_direct_upload_key(key, self.user.pk, purpose="product-image"))
        self.assertFalse(is_own_direct_upload_key(key, self.user.pk + 1, purpose="product-image"))
        self.assertFalse(is_own_direct_upload_key(key, self.user.pk, purpose="ad-video"))
        self.assertFalse(is_own_direct_upload_key("../etc/passwd", self.user.pk))

    def test_all_upload_endpoints_resolve(self):
        for name in (
            "media-upload-initiate", "media-upload-part-url",
            "media-upload-parts", "media-upload-complete", "media-upload-abort",
        ):
            with self.subTest(name=name):
                self.assertTrue(reverse(name).startswith("/api/v1/storage/media/uploads/"))

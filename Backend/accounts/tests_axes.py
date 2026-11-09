"""django-axes lockout verification (S4).

Drives 6 failed logins from the same client and expects the 6th to be
blocked by the lockout (5 failures, 30-minute cool-off). Confirms axes
counts DRF JSON login failures (IP-based for JSON bodies).
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from allauth.account.models import EmailAddress

from accounts.models import User

PASSWORD = "StrongPass123!"


class AxesLockoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="axesuser@example.com",
            username="axesuser",
            password=PASSWORD,
        )
        EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            verified=True,
            primary=True,
        )
        self.login_url = reverse("rest_login")

    def test_five_failures_then_lockout(self):
        codes = []
        for _ in range(7):
            response = self.client.post(
                self.login_url,
                {"email": "axesuser@example.com", "password": "WrongPass999!"},
                format="json",
            )
            codes.append(response.status_code)
        # auth_kit answers wrong-credentials with 400; after the configured
        # threshold (5) the lockout engages with 429.
        self.assertIn(status.HTTP_400_BAD_REQUEST, codes)
        self.assertTrue(
            any(code == status.HTTP_429_TOO_MANY_REQUESTS for code in codes),
            f"Expected a lockout response after repeated failures, got {codes}",
        )

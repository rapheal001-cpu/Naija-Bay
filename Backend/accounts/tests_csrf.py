"""CSRF production-readiness verification matrix (S3).

Covers: valid/missing/invalid CSRF token, missing Origin/Referer, trusted /
untrusted Origin, cookie-authenticated unsafe requests, login/logout/refresh
regression, and the Paystack webhook exemption.
"""

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from allauth.account.models import EmailAddress

from accounts.models import User

PASSWORD = "StrongPass123!"
TRUSTED_ORIGIN = "http://localhost:5173"


def _login(client):
    response = client.post(
        reverse("rest_login"),
        {"email": "csrfuser@example.com", "password": PASSWORD},
        format="json",
        HTTP_ORIGIN=TRUSTED_ORIGIN,
    )
    assert response.status_code == status.HTTP_200_OK, response.content[:200]
    return response


def _csrf_of(client):
    return client.cookies["csrftoken"].value


class CsrfMatrixTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="csrfuser@example.com",
            username="csrfuser",
            password=PASSWORD,
        )
        EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            verified=True,
            primary=True,
        )

    def test_login_flow_gets_cookies_and_is_not_blocked(self):
        response = _login(self.client)
        # An unauthenticated login carries no auth cookies, so CSRF does not apply.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", self.client.cookies)
        self.assertIn("refresh", self.client.cookies)

    def test_csrf_cookie_is_issued_on_get(self):
        self.client.get(reverse("notifications"))
        self.assertIn("csrftoken", self.client.cookies)

    def test_valid_token_allows_unsafe_request(self):
        _login(self.client)
        token = _csrf_of(self.client)
        response = self.client.post(
            reverse("rest_logout"),
            format="json",
            HTTP_ORIGIN=TRUSTED_ORIGIN,
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_missing_token_is_rejected(self):
        _login(self.client)
        response = self.client.post(
            reverse("rest_logout"),
            format="json",
            HTTP_ORIGIN=TRUSTED_ORIGIN,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["code"], "csrf_failed")

    def test_invalid_token_is_rejected(self):
        _login(self.client)
        response = self.client.post(
            reverse("rest_logout"),
            format="json",
            HTTP_ORIGIN=TRUSTED_ORIGIN,
            HTTP_X_CSRFTOKEN="dGVzdA" + "x" * 59,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_origin_and_referer_is_rejected(self):
        _login(self.client)
        token = _csrf_of(self.client)
        response = self.client.post(
            reverse("rest_logout"),
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["code"], "missing_origin")

    def test_untrusted_origin_is_rejected(self):
        _login(self.client)
        token = _csrf_of(self.client)
        response = self.client.post(
            reverse("rest_logout"),
            format="json",
            HTTP_ORIGIN="http://evil.example",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["code"], "untrusted_origin")

    def test_safe_get_needs_no_token(self):
        _login(self.client)
        response = self.client.get(reverse("notifications"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_requires_token_when_cookie_authenticated(self):
        _login(self.client)
        response = self.client.post(
            reverse("rest_logout"),
            format="json",
            HTTP_ORIGIN=TRUSTED_ORIGIN,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_refresh_with_token_works(self):
        _login(self.client)
        token = _csrf_of(self.client)
        response = self.client.post(
            reverse("token_refresh"),
            format="json",
            HTTP_ORIGIN=TRUSTED_ORIGIN,
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", self.client.cookies)


class WebhookExemptionTests(TestCase):
    def test_signed_webhook_path_is_csrf_exempt(self):
        # No cookies, no token: the webhook must reach signature validation
        # (400 signature failure), NOT be stopped by CSRF (403).
        response = Client(enforce_csrf_checks=True).post(
            reverse("paystack-webhook"),
            b"{}",
            content_type="application/json",
        )
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

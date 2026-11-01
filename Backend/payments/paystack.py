"""Thin Paystack client. Only the backend ever sees the secret key.

Development convenience: when ``PAYSTACK_SECRET_KEY`` is empty AND ``DEBUG`` is True,
the client runs in *simulated* mode (no network call, nothing is charged). The rest of
the payment code path (amount checks, idempotency, fulfilment) is identical. Use real
Paystack TEST keys (sk_test_...) to exercise the real checkout page.
"""

import hashlib
import hmac
import logging
from urllib.parse import quote

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://api.paystack.co"
TIMEOUT = 20


class PaystackError(Exception):
    """Paystack could not be reached or rejected the request."""


class PaystackNotFound(PaystackError):
    """Paystack has no transaction with that reference (yet)."""


def is_simulated():
    return (not settings.PAYSTACK_SECRET_KEY) and bool(settings.DEBUG)


def _request(method, path, **kwargs):
    secret = settings.PAYSTACK_SECRET_KEY
    if not secret:
        raise PaystackError("Paystack is not configured on the server.")
    try:
        response = requests.request(
            method,
            f"{BASE_URL}{path}",
            headers={"Authorization": f"Bearer {secret}", "Content-Type": "application/json"},
            timeout=TIMEOUT,
            **kwargs,
        )
        body = response.json()
    except (requests.RequestException, ValueError) as exc:
        # Log the exception type only: never the request (it carries the secret key).
        logger.error("Paystack request failed: %s", exc.__class__.__name__)
        raise PaystackError("Could not reach Paystack.") from exc

    if response.status_code == 404:
        raise PaystackNotFound(body.get("message") or "Transaction not found.")
    if response.status_code >= 400 or not body.get("status"):
        logger.warning("Paystack rejected %s: %s", path, body.get("message"))
        raise PaystackError(body.get("message") or "Paystack rejected the request.")
    return body.get("data") or {}


def initialize_transaction(email, amount_kobo, reference, callback_url, metadata=None):
    if is_simulated():
        logger.warning("Paystack SIMULATED mode: initialize %s", reference)
        return {
            "authorization_url": f"{callback_url}?reference={reference}&simulated=1",
            "access_code": "SIMULATED",
            "reference": reference,
        }
    return _request(
        "POST",
        "/transaction/initialize",
        json={
            "email": email,
            "amount": amount_kobo,
            "currency": "NGN",
            "reference": reference,
            "callback_url": callback_url,
            "metadata": metadata or {},
        },
    )


def verify_transaction(reference, simulated_amount=None):
    if is_simulated():
        logger.warning("Paystack SIMULATED mode: verify %s", reference)
        return {
            "status": "success",
            "reference": reference,
            "amount": simulated_amount,
            "currency": "NGN",
            "id": "SIMULATED",
            "gateway_response": "Simulated payment (development only)",
        }
    return _request("GET", f"/transaction/verify/{quote(reference, safe='')}")


def valid_signature(raw_body, signature):
    """Check Paystack's ``x-paystack-signature`` (HMAC-SHA512 of the raw body)."""
    secret = settings.PAYSTACK_SECRET_KEY
    if not secret or not signature:
        return False
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha512).hexdigest()
    return hmac.compare_digest(expected, signature)

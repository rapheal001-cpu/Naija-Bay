"""Payment + ad-boost business logic.

Import discipline (this is what removes the old products <-> payments cycle):
``products.views`` imports ``expire_boosts_if_due`` from this module, so this module
must never import ``products`` or ``orders`` at module level. Both are imported lazily
inside the functions that need them.
"""

import json
import logging
import uuid
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import APIException, NotFound, ValidationError

from accounts.models import Notifications
from . import paystack
from .models import BoostPlan, ListingBoost, Payment, WebhookEvent

logger = logging.getLogger(__name__)

EXPIRY_CHECK_KEY = "payments:boost-expiry-check"
EXPIRY_CHECK_SECONDS = 60


class PaymentGatewayUnavailable(APIException):
    status_code = 502
    default_detail = "We could not reach the payment provider. Please try again."
    default_code = "gateway_unavailable"


def _notify(user, notification_type, message):
    Notifications.objects.create(user=user, notification_type=notification_type, message=message)


def to_kobo(amount):
    return int((Decimal(amount) * 100).quantize(Decimal("1")))


def _new_reference(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:20].upper()}"


def _callback_url():
    return f"{settings.FRONTEND_URL.rstrip('/')}/payment/callback"


def _start_gateway(payment, email, metadata):
    try:
        data = paystack.initialize_transaction(
            email=email,
            amount_kobo=to_kobo(payment.amount),
            reference=payment.reference,
            callback_url=_callback_url(),
            metadata=metadata,
        )
    except paystack.PaystackError as exc:
        Payment.objects.filter(pk=payment.pk).update(
            status="failed", gateway_response=str(exc)[:200]
        )
        ListingBoost.objects.filter(payment=payment, status="pending").update(status="failed")
        raise PaymentGatewayUnavailable() from exc
    payment.authorization_url = data.get("authorization_url", "")
    payment.save(update_fields=["authorization_url", "updated_at"])
    return payment


# =============================================================================
# ORDER PAYMENTS
# =============================================================================

def initialize_order_payment(user, order_reference):
    from orders.models import Order

    order = Order.objects.filter(reference=order_reference, buyer=user).first()
    if order is None:
        raise NotFound("Order not found.")
    if order.payment_status == "paid":
        raise ValidationError({"detail": "This order has already been paid for."})
    if order.status == "cancelled":
        raise ValidationError({"detail": "This order was cancelled. Please check out again."})

    payment = Payment.objects.create(
        reference=_new_reference("NBO"),
        user=user,
        purpose="order",
        order=order,
        amount=order.total,  # trusted: computed on the server at checkout
        currency=order.currency,
    )
    return _start_gateway(
        payment, user.email, {"purpose": "order", "order": order.reference}
    )


# =============================================================================
# BOOST PAYMENTS
# =============================================================================

def initialize_boost_payment(user, product_id, plan_id):
    from products.models import Product

    try:
        product = Product.objects.filter(pk=int(product_id)).first()
        plan_pk = int(plan_id)
    except (TypeError, ValueError):
        raise ValidationError({"detail": "A valid listing and plan are required."})

    # Hide other sellers' listings entirely: 404, not 403.
    if product is None or product.product_user_id != user.id:
        raise NotFound("Listing not found.")

    plan = BoostPlan.objects.filter(pk=plan_pk, is_active=True).first()
    if plan is None:
        raise ValidationError({"plan": "That boost plan is not available."})
    if product.listing_status != "active":
        raise ValidationError({"detail": "Only active listings can be boosted."})
    if product.is_boosted:
        raise ValidationError(
            {"detail": "This listing is already boosted. You can boost it again once the current boost ends."}
        )

    with transaction.atomic():
        payment = Payment.objects.create(
            reference=_new_reference("NBB"),
            user=user,
            purpose="boost",
            amount=plan.price,  # trusted: read from the plan, never from the client
        )
        ListingBoost.objects.create(product=product, plan=plan, user=user, payment=payment)
    return _start_gateway(
        payment, user.email, {"purpose": "boost", "product": product.pk, "plan": plan.slug}
    )


def activate_boost(payment):
    """Start the promotion for a verified boost payment. Idempotent."""
    from products.models import Product

    boost = (
        ListingBoost.objects.select_for_update()
        .select_related("plan", "product", "user")
        .filter(payment=payment)
        .first()
    )
    if boost is None or boost.status != "pending":
        return boost

    now = timezone.now()
    product = Product.objects.select_for_update().get(pk=boost.product_id)
    start = now
    if product.promoted_until and product.promoted_until > now:
        start = product.promoted_until  # stack on top of any running boost
    expires = start + timedelta(days=boost.plan.duration_days)

    boost.status = "active"
    boost.started_at = now
    boost.expires_at = expires
    boost.save(update_fields=["status", "started_at", "expires_at"])

    # update() on purpose: avoids the product post_save notification signal.
    Product.objects.filter(pk=product.pk).update(
        promoted=True,
        promoted_until=expires,
        boost_level=max(product.boost_level, boost.plan.boost_level),
    )
    _notify(
        boost.user,
        "boost_activated",
        f'Your "{boost.product.product_name}" listing is now boosted ({boost.plan.name}).',
    )
    return boost


def expire_boosts():
    """Switch off boosts whose time is up. Returns how many were expired."""
    from products.models import Product

    now = timezone.now()
    expired = 0
    due = ListingBoost.objects.filter(status="active", expires_at__lte=now).select_related("product", "user")
    for boost in due:
        with transaction.atomic():
            changed = ListingBoost.objects.filter(pk=boost.pk, status="active").update(status="expired")
            if not changed:
                continue
            expired += 1
            still_boosted = ListingBoost.objects.filter(
                product_id=boost.product_id, status="active", expires_at__gt=now
            ).exists()
            if not still_boosted:
                Product.objects.filter(pk=boost.product_id).update(
                    promoted=False, promoted_until=None, boost_level=0
                )
            _notify(
                boost.user,
                "boost_expired",
                f'The boost on "{boost.product.product_name}" has ended. Boost it again to stay on top.',
            )
    # Safety net for rows whose end date passed without a ListingBoost update.
    Product.objects.filter(promoted=True, promoted_until__lte=now).update(
        promoted=False, promoted_until=None, boost_level=0
    )
    return expired


def expire_boosts_if_due(force=False):
    """Cheap hook used by listing views: runs the expiry job at most once a minute."""
    if not force and not cache.add(EXPIRY_CHECK_KEY, 1, EXPIRY_CHECK_SECONDS):
        return 0
    try:
        return expire_boosts()
    except Exception:  # never break a public listing page over housekeeping
        logger.exception("Boost expiry job failed")
        return 0


# =============================================================================
# VERIFICATION (the single place a payment can become "success")
# =============================================================================

def _apply_success(payment, data):
    from orders.services import mark_order_paid

    with transaction.atomic():
        # Conditional UPDATE = atomic idempotency: only one caller wins.
        won = (
            Payment.objects.filter(pk=payment.pk)
            .exclude(status="success")
            .update(
                status="success",
                paid_at=timezone.now(),
                paystack_transaction_id=str(data.get("id", ""))[:64],
                gateway_response=str(data.get("gateway_response", ""))[:200],
                updated_at=timezone.now(),
            )
        )
        if not won:
            return False
        if payment.purpose == "order":
            mark_order_paid(payment.order_id)
        else:
            activate_boost(payment)
        return True


def _apply_non_success(payment, new_status, message):
    Payment.objects.filter(pk=payment.pk).exclude(status="success").update(
        status=new_status, gateway_response=(message or "")[:200], updated_at=timezone.now()
    )
    if new_status == "failed":
        ListingBoost.objects.filter(payment=payment, status="pending").update(status="failed")


def verify_payment(reference, user=None):
    """Ask Paystack what really happened and update our records. Safe to call
    repeatedly (browser callback, webhook, polling) - it never double-fulfils."""
    payment = Payment.objects.filter(reference=reference).first()
    if payment is None or (user is not None and payment.user_id != user.id):
        raise NotFound("Payment not found.")
    if payment.status == "success":
        return payment

    try:
        data = paystack.verify_transaction(
            reference, simulated_amount=to_kobo(payment.amount)
        )
    except paystack.PaystackNotFound:
        # Customer never reached/opened the Paystack page.
        return payment
    except paystack.PaystackError as exc:
        logger.warning("Verify %s failed: %s", reference, exc)
        raise PaymentGatewayUnavailable() from exc

    gateway_status = (data.get("status") or "").lower()

    if gateway_status == "success":
        amount_ok = int(data.get("amount") or -1) == to_kobo(payment.amount)
        currency_ok = (data.get("currency") or "NGN").upper() == payment.currency.upper()
        reference_ok = data.get("reference", reference) == payment.reference
        if not (amount_ok and currency_ok and reference_ok):
            logger.error(
                "Payment %s mismatch: amount_ok=%s currency_ok=%s reference_ok=%s",
                reference, amount_ok, currency_ok, reference_ok,
            )
            _apply_non_success(payment, "failed", "Amount, currency or reference mismatch.")
        else:
            _apply_success(payment, data)
    elif gateway_status in ("failed", "reversed"):
        _apply_non_success(payment, "failed", data.get("gateway_response") or "Payment failed.")
    elif gateway_status == "abandoned":
        _apply_non_success(payment, "abandoned", "Payment was abandoned.")
    # anything else (pending / ongoing / processing / queued) stays pending

    payment.refresh_from_db()
    return payment


# =============================================================================
# WEBHOOK
# =============================================================================

def process_webhook(payload):
    """Handle a signature-verified webhook. Returns a short result string."""
    event = payload.get("event", "")
    data = payload.get("data") or {}
    reference = data.get("reference", "")

    if event != "charge.success" or not reference:
        return "ignored"
    if not Payment.objects.filter(reference=reference).exists():
        logger.info("Webhook for unknown reference %s ignored", reference)
        return "unknown"

    event_key = f"{event}:{data.get('id') or reference}"[:120]
    # Event row + processing share one transaction: if verification fails the row
    # rolls back and Paystack's retry is processed again instead of skipped.
    # The status flag keeps the outcome auditable (processing -> succeeded/failed).
    with transaction.atomic():
        record, created = WebhookEvent.objects.get_or_create(
            event_key=event_key,
            defaults={"event_type": event, "reference": reference, "status": "processing"},
        )
        if not created:
            return "duplicate"
        try:
            verify_payment(reference)  # re-checks with Paystack; body is never trusted
        except Exception as exc:
            record.status = "failed"
            record.error = str(exc)[:2000]
            record.processed_at = timezone.now()
            record.save(update_fields=["status", "error", "processed_at"])
            raise
        record.status = "succeeded"
        record.processed_at = timezone.now()
        record.save(update_fields=["status", "error", "processed_at"])
    return "processed"


def parse_webhook_body(raw_body):
    try:
        return json.loads(raw_body)
    except ValueError:
        return None

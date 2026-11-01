from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


# =============================================================================
# PAYMENT (one Paystack transaction)
# =============================================================================

class Payment(models.Model):
    PURPOSE_CHOICES = [("order", "Order"), ("boost", "Ad Boost")]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("abandoned", "Abandoned"),
    ]

    reference = models.CharField(_("Reference"), max_length=64, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name=_("User"),
    )
    purpose = models.CharField(_("Purpose"), max_length=10, choices=PURPOSE_CHOICES, db_index=True)
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name=_("Order"),
    )
    amount = models.DecimalField(_("Amount (NGN)"), max_digits=14, decimal_places=2)
    currency = models.CharField(_("Currency"), max_length=3, default="NGN")
    status = models.CharField(
        _("Status"), max_length=10, choices=STATUS_CHOICES, default="pending", db_index=True
    )
    authorization_url = models.URLField(_("Authorization URL"), max_length=500, blank=True)
    paystack_transaction_id = models.CharField(_("Paystack Transaction ID"), max_length=64, blank=True)
    gateway_response = models.CharField(_("Gateway Response"), max_length=200, blank=True)
    paid_at = models.DateTimeField(_("Paid At"), null=True, blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        return f"{self.reference} ({self.status})"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["purpose", "status"]),
        ]


class WebhookEvent(models.Model):
    """One row per processed Paystack webhook delivery (idempotency guard)."""

    event_key = models.CharField(_("Event Key"), max_length=120, unique=True)
    event_type = models.CharField(_("Event Type"), max_length=60)
    reference = models.CharField(_("Reference"), max_length=64, blank=True)
    received_at = models.DateTimeField(_("Received At"), auto_now_add=True)

    def __str__(self):
        return self.event_key

    class Meta:
        ordering = ["-received_at"]
        verbose_name = _("Webhook Event")
        verbose_name_plural = _("Webhook Events")


# =============================================================================
# AD BOOSTING
# =============================================================================

class BoostPlan(models.Model):
    """A purchasable promotion tier. Fully editable from the Django admin."""

    name = models.CharField(_("Name"), max_length=60)
    slug = models.SlugField(_("Slug"), max_length=60, unique=True)
    description = models.CharField(_("Description"), max_length=200, blank=True)
    price = models.DecimalField(
        _("Price (NGN)"), max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("100.00"))],
    )
    duration_days = models.PositiveIntegerField(_("Duration (days)"), validators=[MinValueValidator(1)])
    boost_level = models.PositiveSmallIntegerField(
        _("Boost Level"), default=1, validators=[MinValueValidator(1)],
        help_text=_("Higher levels rank above lower levels in search results."),
    )
    benefits = models.JSONField(_("Benefits"), default=list, blank=True)
    is_active = models.BooleanField(_("Active"), default=True, db_index=True)
    sort_order = models.PositiveSmallIntegerField(_("Sort Order"), default=0)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{self.name} - NGN {self.price} / {self.duration_days}d"

    class Meta:
        ordering = ["sort_order", "price"]
        verbose_name = _("Boost Plan")
        verbose_name_plural = _("Boost Plans")


class ListingBoost(models.Model):
    STATUS_CHOICES = [
        ("pending", "Awaiting payment"),
        ("active", "Active"),
        ("expired", "Expired"),
        ("failed", "Payment failed"),
    ]

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="boosts",
        verbose_name=_("Product"),
    )
    plan = models.ForeignKey(
        BoostPlan, on_delete=models.PROTECT, related_name="boosts", verbose_name=_("Plan")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="boosts",
        verbose_name=_("Seller"),
    )
    # OneToOne => a single payment can only ever activate a single boost.
    payment = models.OneToOneField(
        Payment, on_delete=models.PROTECT, related_name="boost", verbose_name=_("Payment")
    )
    status = models.CharField(
        _("Status"), max_length=10, choices=STATUS_CHOICES, default="pending", db_index=True
    )
    started_at = models.DateTimeField(_("Started At"), null=True, blank=True)
    expires_at = models.DateTimeField(_("Expires At"), null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{self.product_id} - {self.plan.name} ({self.status})"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Listing Boost")
        verbose_name_plural = _("Listing Boosts")
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status", "expires_at"]),
        ]

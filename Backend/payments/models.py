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
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gte=0),
                name="payment_amount_non_negative",
            ),
        ]


class WebhookEvent(models.Model):
    """One row per processed Paystack webhook delivery (idempotency guard)."""

    EVENT_STATUS_CHOICES = [
        ("processing", "Processing"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
    ]

    event_key = models.CharField(_("Event Key"), max_length=120, unique=True)
    event_type = models.CharField(_("Event Type"), max_length=60)
    reference = models.CharField(_("Reference"), max_length=64, blank=True)
    status = models.CharField(
        _("Status"), max_length=20, choices=EVENT_STATUS_CHOICES,
        default="succeeded", db_index=True,
    )
    error = models.TextField(_("Error"), blank=True, default="")
    received_at = models.DateTimeField(_("Received At"), auto_now_add=True)
    processed_at = models.DateTimeField(_("Processed At"), null=True, blank=True)

    def __str__(self):
        return self.event_key

    class Meta:
        ordering = ["-received_at"]
        verbose_name = _("Webhook Event")
        verbose_name_plural = _("Webhook Events")
        indexes = [
            models.Index(fields=["status", "-received_at"]),
        ]


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


# =============================================================================
# CREDITS WALLET  (Jiji: 1 Credit = NGN 1, used only for premium services)
# =============================================================================

class CreditAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="credit_account",
        verbose_name=_("User"),
    )
    balance = models.DecimalField(
        _("Balance"), max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        return f"{self.user_id}: {self.balance}"

    class Meta:
        verbose_name = _("Credit Account")
        verbose_name_plural = _("Credit Accounts")


class CreditTransaction(models.Model):
    TYPE_CHOICES = [
        ("topup", "Top up"),
        ("spend", "Spend"),
        ("referral", "Referral bonus"),
        ("adjustment", "Adjustment"),
    ]

    account = models.ForeignKey(
        CreditAccount, on_delete=models.PROTECT, related_name="transactions", verbose_name=_("Account")
    )
    transaction_type = models.CharField(_("Type"), max_length=12, choices=TYPE_CHOICES, db_index=True)
    amount = models.DecimalField(_("Amount"), max_digits=14, decimal_places=2)
    reference = models.CharField(_("Reference"), max_length=64, blank=True, db_index=True)
    description = models.CharField(_("Description"), max_length=200, blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.transaction_type} {self.amount} ({self.account_id})"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Credit Transaction")
        verbose_name_plural = _("Credit Transactions")
        indexes = [
            models.Index(fields=["account", "-created_at"]),
        ]


class ReferralBonus(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("credited", "Credited"),
        ("forfeited", "Forfeited"),
    ]

    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referrals_made",
        verbose_name=_("Referrer"),
    )
    referred = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referral",
        verbose_name=_("Referred User"),
    )
    amount = models.DecimalField(_("Amount"), max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(
        _("Status"), max_length=10, choices=STATUS_CHOICES, default="pending", db_index=True
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.referrer_id} -> {self.referred_id} ({self.status})"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Referral Bonus")
        verbose_name_plural = _("Referral Bonuses")
        indexes = [
            models.Index(fields=["referrer", "status", "-created_at"]),
        ]


# =============================================================================
# BOOST AUTO-RENEWAL  (Paystack mandate, 5% cheaper renewal)
# =============================================================================

class BoostAutoRenewal(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("paused", "Paused"),
        ("cancelled", "Cancelled"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="boost_auto_renewals",
        verbose_name=_("User"),
    )
    plan = models.ForeignKey(
        BoostPlan, on_delete=models.PROTECT, related_name="auto_renewals", verbose_name=_("Plan")
    )
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="auto_renewals", verbose_name=_("Product")
    )
    mandate_reference = models.CharField(_("Mandate Reference"), max_length=100, blank=True)
    status = models.CharField(
        _("Status"), max_length=10, choices=STATUS_CHOICES, default="active", db_index=True
    )
    next_charge_at = models.DateTimeField(_("Next Charge At"), null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"Auto-renew {self.plan_id} for {self.product_id} ({self.status})"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Boost Auto-Renewal")
        verbose_name_plural = _("Boost Auto-Renewals")
        indexes = [
            models.Index(fields=["user", "status", "-created_at"]),
        ]


# =============================================================================
# PRO SALES  (Jiji pay-per-click campaigns with bid groups)
# =============================================================================

class ProSalesCampaign(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("paused", "Paused"),
        ("ended", "Ended"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pro_sales_campaigns",
        verbose_name=_("User"),
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="pro_sales_campaigns",
        verbose_name=_("Product"),
    )
    name = models.CharField(_("Campaign Name"), max_length=80)
    daily_budget = models.DecimalField(
        _("Daily Budget"), max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("100.00"))],
    )
    bid_amount = models.DecimalField(
        _("Bid per Click"), max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("1.00"))],
    )
    status = models.CharField(
        _("Status"), max_length=10, choices=STATUS_CHOICES, default="active", db_index=True
    )
    clicks = models.PositiveIntegerField(_("Clicks"), default=0)
    impressions = models.PositiveIntegerField(_("Impressions"), default=0)
    spend = models.DecimalField(_("Spend"), max_digits=14, decimal_places=2, default=Decimal("0.00"))
    started_at = models.DateTimeField(_("Started At"), null=True, blank=True)
    ends_at = models.DateTimeField(_("Ends At"), null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.name} ({self.status})"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Pro Sales Campaign")
        verbose_name_plural = _("Pro Sales Campaigns")
        indexes = [
            models.Index(fields=["user", "status", "-created_at"]),
        ]

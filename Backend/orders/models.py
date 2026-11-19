import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from NaijaBay.utils import STATE_CHOICES


# =============================================================================
# CART
# =============================================================================

class Cart(models.Model):
    """One persistent cart per authenticated user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name=_("User"),
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        return f"Cart of {self.user}"

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items", verbose_name=_("Cart")
    )
    # CASCADE: when a listing is deleted it silently disappears from carts.
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name=_("Product"),
    )
    quantity = models.PositiveIntegerField(
        _("Quantity"), default=1, validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        return f"{self.quantity} x {self.product_id}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"], name="unique_product_per_cart"
            ),
        ]


# =============================================================================
# ORDER
# =============================================================================

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("refunded", "Refunded"),
    ]

    reference = models.CharField(
        _("Reference"), max_length=24, unique=True, editable=False, db_index=True
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
        verbose_name=_("Buyer"),
    )
    status = models.CharField(
        _("Order Status"), max_length=12, choices=STATUS_CHOICES, default="pending", db_index=True
    )
    payment_status = models.CharField(
        _("Payment Status"), max_length=10, choices=PAYMENT_STATUS_CHOICES, default="unpaid", db_index=True
    )
    subtotal = models.DecimalField(_("Subtotal"), max_digits=14, decimal_places=2, default=Decimal("0.00"))
    delivery_fee = models.DecimalField(_("Delivery Fee"), max_digits=14, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(_("Total"), max_digits=14, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(_("Currency"), max_length=3, default="NGN")

    # Delivery details
    recipient_name = models.CharField(_("Recipient Name"), max_length=80)
    phone = models.CharField(_("Phone"), max_length=20)
    address = models.TextField(_("Delivery Address"))
    state = models.CharField(_("State"), max_length=25, choices=STATE_CHOICES, blank=True)
    note = models.CharField(_("Note"), max_length=300, blank=True)

    # -------------------------------------------------------------------------
    # Safe Deal (escrow): money is held until the buyer confirms delivery.
    # -------------------------------------------------------------------------
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders_as_seller",
        verbose_name=_("Seller"),
    )
    is_safe_deal = models.BooleanField(_("Safe Deal"), default=False, db_index=True)
    ESCROW_STATUS_CHOICES = [
        ("none", "Not a Safe Deal"),
        ("paid", "Paid — awaiting shipment"),
        ("shipped", "Shipped / handed to courier"),
        ("delivered", "Delivered — buyer confirmation window open"),
        ("confirmed", "Confirmed — payment released"),
        ("disputed", "Disputed — under review"),
        ("refunded", "Refunded"),
    ]
    escrow_status = models.CharField(
        _("Escrow Status"), max_length=12, choices=ESCROW_STATUS_CHOICES,
        default="none", db_index=True,
    )
    delivery_service = models.CharField(_("Delivery Service"), max_length=60, blank=True)
    tracking_number = models.CharField(_("Tracking Number"), max_length=80, blank=True)
    shipped_at = models.DateTimeField(_("Shipped At"), null=True, blank=True)
    delivered_at = models.DateTimeField(_("Delivered At"), null=True, blank=True)
    confirm_deadline = models.DateTimeField(_("Confirm Deadline"), null=True, blank=True, db_index=True)
    buyer_confirmed_at = models.DateTimeField(_("Buyer Confirmed At"), null=True, blank=True)
    dispute_opened_at = models.DateTimeField(_("Dispute Opened At"), null=True, blank=True)
    dispute_reason = models.TextField(_("Dispute Reason"), blank=True)
    seller_payout_at = models.DateTimeField(_("Seller Payout At"), null=True, blank=True)
    payout_reference = models.CharField(_("Payout Reference"), max_length=64, blank=True)

    paid_at = models.DateTimeField(_("Paid At"), null=True, blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    @staticmethod
    def generate_reference():
        while True:
            reference = f"NB-{uuid.uuid4().hex[:10].upper()}"
            if not Order.objects.filter(reference=reference).exists():
                return reference

    def __str__(self):
        return f"{self.reference} ({self.status}/{self.payment_status})"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        indexes = [
            models.Index(fields=["buyer", "-created_at"]),
            models.Index(fields=["buyer", "status", "payment_status"]),
        ]


class OrderItem(models.Model):
    STATUS_CHOICES = Order.STATUS_CHOICES

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name=_("Order")
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
        verbose_name=_("Product"),
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sales",
        verbose_name=_("Seller"),
    )
    # Snapshots so the order stays correct if the listing changes or is deleted.
    product_name = models.CharField(_("Product Name"), max_length=200)
    product_slug = models.CharField(_("Product Slug"), max_length=200, blank=True)
    unit_price = models.DecimalField(_("Unit Price"), max_digits=15, decimal_places=2)
    quantity = models.PositiveIntegerField(_("Quantity"), validators=[MinValueValidator(1)])
    line_total = models.DecimalField(_("Line Total"), max_digits=15, decimal_places=2)
    status = models.CharField(
        _("Item Status"), max_length=12, choices=STATUS_CHOICES, default="pending", db_index=True
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

    class Meta:
        ordering = ["id"]
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        indexes = [
            models.Index(fields=["seller", "-created_at"]),
        ]

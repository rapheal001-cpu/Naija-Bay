from rest_framework import serializers

from NaijaBay.utils import STATE_CHOICES
from .models import Order, OrderItem
from .services import cart_items, cart_totals, item_issue


def _first_image(request, product):
    if product is None:
        return None
    image = next(iter(product.images.all()), None)
    if image is None:
        return None
    url = image.image.url
    return request.build_absolute_uri(url) if request else url


# =============================================================================
# CART
# =============================================================================

class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(source="product.id")
    slug = serializers.CharField(source="product.product_slug")
    name = serializers.CharField(source="product.product_name")
    image = serializers.SerializerMethodField()
    seller = serializers.CharField(source="product.product_user.username")
    unit_price = serializers.DecimalField(
        source="product.price", max_digits=15, decimal_places=2
    )
    quantity = serializers.IntegerField()
    stock = serializers.IntegerField(source="product.quantity")
    line_total = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()
    issue = serializers.SerializerMethodField()

    def get_image(self, obj):
        return _first_image(self.context.get("request"), obj.product)

    def get_line_total(self, obj):
        return obj.product.price * obj.quantity

    def get_issue(self, obj):
        return item_issue(obj)

    def get_available(self, obj):
        return item_issue(obj) is None


class CartSerializer(serializers.Serializer):
    """Serialises a ``Cart`` with live, backend-computed totals."""

    def to_representation(self, cart):
        items = list(cart_items(cart))
        return {
            "items": CartItemSerializer(items, many=True, context=self.context).data,
            **cart_totals(items),
        }


# =============================================================================
# CHECKOUT INPUT
# =============================================================================

class ShippingSerializer(serializers.Serializer):
    recipient_name = serializers.CharField(max_length=80)
    phone = serializers.RegexField(
        r"^\+?[0-9]{10,15}$",
        error_messages={"invalid": "Enter a valid phone number (10-15 digits)."},
    )
    address = serializers.CharField(min_length=8, max_length=500)
    state = serializers.ChoiceField(choices=[c for c in STATE_CHOICES if c[0]])
    note = serializers.CharField(max_length=300, required=False, allow_blank=True, default="")

    def validate_recipient_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Enter the recipient's name.")
        return value

    def validate_phone(self, value):
        return value.replace(" ", "")


# =============================================================================
# ORDERS
# =============================================================================

class OrderItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    seller_username = serializers.CharField(source="seller.username", default=None, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id", "product_name", "product_slug", "image", "unit_price",
            "quantity", "line_total", "status", "seller_username",
        ]

    def get_image(self, obj):
        return _first_image(self.context.get("request"), obj.product)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    last_payment_status = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    can_pay = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "reference", "status", "payment_status", "last_payment_status",
            "subtotal", "delivery_fee", "total", "currency",
            "recipient_name", "phone", "address", "state", "note",
            "items", "can_cancel", "can_pay", "paid_at", "created_at",
        ]

    def get_last_payment_status(self, obj):
        # Prefer the prefetched payments (order lists) to avoid a per-row
        # ordered query; fall back only for single-object responses.
        cached = obj._prefetched_objects_cache.get("payments") if hasattr(obj, "_prefetched_objects_cache") else None
        if cached is not None:
            if not cached:
                return None
            latest = max(cached, key=lambda p: (p.created_at or p.pk))
            return latest.status
        payment = obj.payments.order_by("-created_at").first()
        return payment.status if payment else None

    def get_can_cancel(self, obj):
        return obj.payment_status == "unpaid" and obj.status == "pending"

    def get_can_pay(self, obj):
        return obj.payment_status == "unpaid" and obj.status != "cancelled"


class SalesItemSerializer(serializers.ModelSerializer):
    """Seller view of one line of a PAID order. Delivery details are included
    because the seller needs them to ship; unpaid orders never reach this."""

    image = serializers.SerializerMethodField()
    order_reference = serializers.CharField(source="order.reference")
    order_status = serializers.CharField(source="order.status")
    buyer_username = serializers.CharField(source="order.buyer.username", default=None)
    recipient_name = serializers.CharField(source="order.recipient_name")
    phone = serializers.CharField(source="order.phone")
    address = serializers.CharField(source="order.address")
    state = serializers.CharField(source="order.state")
    note = serializers.CharField(source="order.note")
    paid_at = serializers.DateTimeField(source="order.paid_at")
    next_statuses = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id", "order_reference", "order_status", "product_name", "product_slug",
            "image", "unit_price", "quantity", "line_total", "status", "next_statuses",
            "buyer_username", "recipient_name", "phone", "address", "state", "note",
            "paid_at", "created_at",
        ]

    def get_image(self, obj):
        return _first_image(self.context.get("request"), obj.product)

    def get_next_statuses(self, obj):
        from .services import ITEM_TRANSITIONS
        return ITEM_TRANSITIONS.get(obj.status, [])


class ItemStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["processing", "shipped", "delivered", "cancelled"])

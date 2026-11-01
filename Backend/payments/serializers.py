from django.utils import timezone
from rest_framework import serializers

from .models import BoostPlan, ListingBoost, Payment


class BoostPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoostPlan
        fields = [
            "id", "name", "slug", "description", "price",
            "duration_days", "boost_level", "benefits",
        ]


class InitializeBoostSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    plan_id = serializers.IntegerField()


class ListingBoostSerializer(serializers.ModelSerializer):
    plan = BoostPlanSerializer(read_only=True)
    product = serializers.SerializerMethodField()
    effective_status = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    payment_status = serializers.CharField(source="payment.status", read_only=True)
    payment_reference = serializers.CharField(source="payment.reference", read_only=True)

    class Meta:
        model = ListingBoost
        fields = [
            "id", "product", "plan", "status", "effective_status", "days_remaining",
            "started_at", "expires_at", "payment_status", "payment_reference", "created_at",
        ]

    def get_product(self, obj):
        image = next(iter(obj.product.images.all()), None)
        request = self.context.get("request")
        url = None
        if image:
            url = request.build_absolute_uri(image.image.url) if request else image.image.url
        return {
            "id": obj.product_id,
            "slug": obj.product.product_slug,
            "name": obj.product.product_name,
            "image": url,
        }

    def get_effective_status(self, obj):
        # Reads correctly even before the background expiry job has run.
        if obj.status == "active" and obj.expires_at and obj.expires_at <= timezone.now():
            return "expired"
        return obj.status

    def get_days_remaining(self, obj):
        if obj.status != "active" or not obj.expires_at:
            return 0
        seconds = (obj.expires_at - timezone.now()).total_seconds()
        return max(0, int(-(-seconds // 86400)))  # ceil


MESSAGES = {
    "success": "Payment confirmed. Thank you!",
    "pending": "We have not received confirmation of this payment yet.",
    "failed": "The payment was not successful.",
    "abandoned": "The payment was not completed.",
}


def payment_payload(payment, request=None):
    """Result returned to the browser callback page. ``status`` comes ONLY from
    our own database, which is only ever written after server-side verification."""
    boost = getattr(payment, "boost", None)
    return {
        "reference": payment.reference,
        "status": payment.status,
        "purpose": payment.purpose,
        "amount": payment.amount,
        "currency": payment.currency,
        "message": MESSAGES.get(payment.status, ""),
        "order_reference": payment.order.reference if payment.order_id else None,
        "boost": (
            ListingBoostSerializer(boost, context={"request": request}).data
            if boost is not None
            else None
        ),
    }

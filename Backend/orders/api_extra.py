"""Safe Deal (escrow) APIs — hold payment until the buyer confirms delivery."""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers, status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from NaijaBay.pagination import StandardPagination
from .models import Order


class SafeDealOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id", "reference", "buyer", "seller", "status", "payment_status",
            "escrow_status", "total", "recipient_name", "phone", "address", "state",
            "delivery_service", "tracking_number", "shipped_at", "delivered_at",
            "confirm_deadline", "buyer_confirmed_at", "dispute_opened_at",
            "dispute_reason", "seller_payout_at", "payout_reference",
            "created_at", "updated_at",
        ]
        read_only_fields = fields


def _get_order(reference):
    return get_object_or_404(Order, reference=reference, is_safe_deal=True)


def _is_seller(order, user):
    if order.seller_id == user.id:
        return True
    return order.items.filter(seller=user).exists()


@extend_schema_view(get=extend_schema(tags=["Safe Deal"]))
class SafeDealListAPIView(ListAPIView):
    serializer_class = SafeDealOrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return (
            Order.objects.filter(is_safe_deal=True)
            .filter(Q(buyer=self.request.user) | Q(seller=self.request.user))
            .select_related("buyer", "seller")
            .order_by("-created_at")
        )


class _BaseSafeDealView(APIView):
    permission_classes = [IsAuthenticated]

    def _order(self, request):
        return _get_order(self.kwargs["reference"])


@extend_schema_view(post=extend_schema(tags=["Safe Deal"], operation_id="Accept Safe Deal order"))
class SafeDealAcceptAPIView(_BaseSafeDealView):
    def post(self, request, reference):
        order = self._order(request)
        if not _is_seller(order, request.user):
            return Response({"detail": "Only the seller can accept an order."}, status=status.HTTP_403_FORBIDDEN)
        if order.escrow_status != "paid":
            return Response({"detail": "Order is not awaiting shipment."}, status=status.HTTP_400_BAD_REQUEST)
        order.delivery_service = request.data.get("delivery_service", "")
        order.status = "processing"
        order.escrow_status = "shipped"
        order.shipped_at = timezone.now()
        order.save(update_fields=["delivery_service", "status", "escrow_status", "shipped_at", "updated_at"])
        return Response(SafeDealOrderSerializer(order).data)


@extend_schema_view(post=extend_schema(tags=["Safe Deal"], operation_id="Submit tracking number"))
class SafeDealTrackingAPIView(_BaseSafeDealView):
    def post(self, request, reference):
        order = self._order(request)
        if not _is_seller(order, request.user):
            return Response({"detail": "Only the seller can submit tracking."}, status=status.HTTP_403_FORBIDDEN)
        tracking = request.data.get("tracking_number", "").strip()
        if not tracking:
            return Response({"detail": "tracking_number is required."}, status=status.HTTP_400_BAD_REQUEST)
        order.tracking_number = tracking
        order.escrow_status = "shipped"
        order.shipped_at = order.shipped_at or timezone.now()
        order.save(update_fields=["tracking_number", "escrow_status", "shipped_at", "updated_at"])
        return Response(SafeDealOrderSerializer(order).data)


@extend_schema_view(post=extend_schema(tags=["Safe Deal"], operation_id="Mark order delivered"))
class SafeDealMarkDeliveredAPIView(_BaseSafeDealView):
    def post(self, request, reference):
        order = self._order(request)
        if not _is_seller(order, request.user):
            return Response({"detail": "Only the seller can mark delivered."}, status=status.HTTP_403_FORBIDDEN)
        order.status = "delivered"
        order.escrow_status = "delivered"
        order.delivered_at = timezone.now()
        order.confirm_deadline = order.delivered_at + timedelta(hours=24)
        order.save(update_fields=["status", "escrow_status", "delivered_at", "confirm_deadline", "updated_at"])
        return Response(SafeDealOrderSerializer(order).data)


@extend_schema_view(post=extend_schema(tags=["Safe Deal"], operation_id="Confirm receipt"))
class SafeDealConfirmAPIView(_BaseSafeDealView):
    def post(self, request, reference):
        order = self._order(request)
        if order.buyer_id != request.user.id:
            return Response({"detail": "Only the buyer can confirm receipt."}, status=status.HTTP_403_FORBIDDEN)
        if order.escrow_status != "delivered":
            return Response({"detail": "Order has not been marked delivered."}, status=status.HTTP_400_BAD_REQUEST)
        order.buyer_confirmed_at = timezone.now()
        order.escrow_status = "confirmed"
        order.payment_status = "paid"
        order.seller_payout_at = timezone.now()
        order.save(update_fields=[
            "buyer_confirmed_at", "escrow_status", "payment_status", "seller_payout_at", "updated_at",
        ])
        return Response(SafeDealOrderSerializer(order).data)


@extend_schema_view(post=extend_schema(tags=["Safe Deal"], operation_id="Report a problem"))
class SafeDealProblemAPIView(_BaseSafeDealView):
    def post(self, request, reference):
        order = self._order(request)
        if order.buyer_id != request.user.id:
            return Response({"detail": "Only the buyer can report a problem."}, status=status.HTTP_403_FORBIDDEN)
        reason = request.data.get("reason", "").strip()
        if not reason:
            return Response({"detail": "reason is required."}, status=status.HTTP_400_BAD_REQUEST)
        order.dispute_reason = reason
        order.dispute_opened_at = timezone.now()
        order.escrow_status = "disputed"
        order.save(update_fields=["dispute_reason", "dispute_opened_at", "escrow_status", "updated_at"])
        return Response(SafeDealOrderSerializer(order).data)


@extend_schema_view(post=extend_schema(tags=["Safe Deal"], operation_id="Extend delivery deadline"))
class SafeDealExtendAPIView(_BaseSafeDealView):
    def post(self, request, reference):
        order = self._order(request)
        if not _is_seller(order, request.user):
            return Response({"detail": "Only the seller can extend a deadline."}, status=status.HTTP_403_FORBIDDEN)
        if getattr(order, "_deadline_extended", False):
            return Response({"detail": "Deadline can only be extended once."}, status=status.HTTP_400_BAD_REQUEST)
        # One extension only: marker stored in dispute_reason-free note field via tracking prefix.
        if order.note and "deadline_extended" in order.note:
            return Response({"detail": "Deadline can only be extended once."}, status=status.HTTP_400_BAD_REQUEST)
        order.note = f"{order.note} deadline_extended".strip()
        if order.confirm_deadline:
            order.confirm_deadline += timedelta(days=7)
        order.save(update_fields=["note", "confirm_deadline", "updated_at"])
        return Response(SafeDealOrderSerializer(order).data)

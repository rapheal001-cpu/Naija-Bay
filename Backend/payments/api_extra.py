"""Extra Jiji-style monetisation APIs: credits, referrals, auto-renewal, Pro Sales."""

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from NaijaBay.pagination import StandardPagination
from .models import (
    CreditAccount, CreditTransaction, ReferralBonus,
    BoostAutoRenewal, ProSalesCampaign,
)


# ---------------------------------------------------------------------------
# CREDITS WALLET
# ---------------------------------------------------------------------------

class CreditTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditTransaction
        fields = ["id", "transaction_type", "amount", "reference", "description", "created_at"]
        read_only_fields = fields


@extend_schema_view(get=extend_schema(tags=["Credits"], operation_id="My credit balance"))
class CreditAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        account, _ = CreditAccount.objects.get_or_create(user=request.user)
        recent = CreditTransaction.objects.filter(account=account).order_by("-created_at")[:20]
        return Response({
            "balance": account.balance,
            "transactions": CreditTransactionSerializer(recent, many=True).data,
        })


@extend_schema_view(get=extend_schema(tags=["Credits"], operation_id="My credit transactions"))
class CreditTransactionListAPIView(ListAPIView):
    serializer_class = CreditTransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return CreditTransaction.objects.filter(account__user=self.request.user).order_by("-created_at")


# ---------------------------------------------------------------------------
# REFERRALS
# ---------------------------------------------------------------------------

class ReferralBonusSerializer(serializers.ModelSerializer):
    referred_username = serializers.CharField(source="referred.username", read_only=True)

    class Meta:
        model = ReferralBonus
        fields = ["id", "referrer", "referred", "referred_username", "amount", "status", "created_at"]
        read_only_fields = fields


@extend_schema_view(get=extend_schema(tags=["Referrals"], operation_id="My referrals"))
class ReferralListAPIView(ListAPIView):
    serializer_class = ReferralBonusSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return ReferralBonus.objects.filter(referrer=self.request.user).select_related("referred").order_by("-created_at")


# ---------------------------------------------------------------------------
# BOOST AUTO-RENEWAL
# ---------------------------------------------------------------------------

class BoostAutoRenewalSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    class Meta:
        model = BoostAutoRenewal
        fields = [
            "id", "user", "plan", "plan_name", "product", "mandate_reference",
            "status", "next_charge_at", "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]


@extend_schema_view(
    get=extend_schema(tags=["Auto-renewal"]),
    post=extend_schema(tags=["Auto-renewal"], operation_id="Set up boost auto-renewal"),
)
class BoostAutoRenewalListCreateAPIView(ListAPIView, CreateAPIView):
    serializer_class = BoostAutoRenewalSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return BoostAutoRenewal.objects.filter(user=self.request.user).select_related("plan").order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status="active")


@extend_schema_view(
    patch=extend_schema(tags=["Auto-renewal"]),
    delete=extend_schema(tags=["Auto-renewal"]),
)
class BoostAutoRenewalDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = BoostAutoRenewalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BoostAutoRenewal.objects.filter(user=self.request.user)


# ---------------------------------------------------------------------------
# PRO SALES (pay-per-click)
# ---------------------------------------------------------------------------

class ProSalesCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProSalesCampaign
        fields = [
            "id", "user", "product", "name", "daily_budget", "bid_amount",
            "status", "clicks", "impressions", "spend", "started_at", "ends_at", "created_at",
        ]
        read_only_fields = ["id", "user", "clicks", "impressions", "spend", "created_at"]


@extend_schema_view(
    get=extend_schema(tags=["Pro Sales"]),
    post=extend_schema(tags=["Pro Sales"], operation_id="Create Pro Sales campaign"),
)
class ProSalesCampaignListCreateAPIView(ListAPIView, CreateAPIView):
    serializer_class = ProSalesCampaignSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return ProSalesCampaign.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        from django.utils import timezone
        serializer.save(user=self.request.user, status="active", started_at=timezone.now())


@extend_schema_view(
    patch=extend_schema(tags=["Pro Sales"]),
    delete=extend_schema(tags=["Pro Sales"]),
)
class ProSalesCampaignDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProSalesCampaignSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProSalesCampaign.objects.filter(user=self.request.user)

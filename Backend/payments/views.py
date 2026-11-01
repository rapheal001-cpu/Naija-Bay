import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from NaijaBay.pagination import StandardPagination
from NaijaBay.throttling import BoostThrottling, CheckoutThrottling, PaymentVerifyThrottling
from . import paystack, services
from .models import BoostPlan, ListingBoost
from .serializers import (
    BoostPlanSerializer,
    InitializeBoostSerializer,
    ListingBoostSerializer,
    payment_payload,
)

logger = logging.getLogger(__name__)


def _init_response(payment):
    return Response(
        {
            "reference": payment.reference,
            "authorization_url": payment.authorization_url,
            "amount": payment.amount,
            "currency": payment.currency,
        },
        status=status.HTTP_201_CREATED,
    )


# =============================================================================
# ORDER PAYMENT
# =============================================================================

@extend_schema_view(post=extend_schema(tags=["Payments"], operation_id="Initialize Order Payment"))
class InitializeOrderPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [CheckoutThrottling]
    serializer_class = BoostPlanSerializer  # schema placeholder (no request body)

    def post(self, request, reference):
        payment = services.initialize_order_payment(request.user, reference)
        return _init_response(payment)


# =============================================================================
# AD BOOSTING
# =============================================================================

@extend_schema_view(get=extend_schema(tags=["Payments"], operation_id="Boost Plans"))
class BoostPlansListAPIView(ListAPIView):
    serializer_class = BoostPlanSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return BoostPlan.objects.filter(is_active=True)


@extend_schema_view(
    post=extend_schema(
        tags=["Payments"], operation_id="Initialize Boost Payment",
        request=InitializeBoostSerializer,
    )
)
class InitializeBoostAPIView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [BoostThrottling]
    serializer_class = InitializeBoostSerializer

    def post(self, request):
        serializer = InitializeBoostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = services.initialize_boost_payment(
            request.user,
            serializer.validated_data["product_id"],
            serializer.validated_data["plan_id"],
        )
        return _init_response(payment)


@extend_schema_view(get=extend_schema(tags=["Payments"], operation_id="My Boosts"))
class MyBoostsListAPIView(ListAPIView):
    serializer_class = ListingBoostSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [BoostThrottling]
    pagination_class = StandardPagination

    def get_queryset(self):
        services.expire_boosts_if_due()
        queryset = (
            ListingBoost.objects.filter(user=self.request.user)
            .select_related("plan", "product", "payment")
            .prefetch_related("product__images")
            .order_by("-created_at")
        )
        wanted = (self.request.query_params.get("status") or "").lower()
        if wanted in {"active", "expired", "pending", "failed"}:
            queryset = queryset.filter(status=wanted)
        return queryset


# =============================================================================
# VERIFY (browser callback) & WEBHOOK (Paystack -> server)
# =============================================================================

@extend_schema_view(get=extend_schema(tags=["Payments"], operation_id="Verify Payment"))
class VerifyPaymentAPIView(APIView):
    """Verifies with Paystack on the server and reports OUR recorded status."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [PaymentVerifyThrottling]
    serializer_class = ListingBoostSerializer  # schema placeholder

    def get(self, request, reference):
        payment = services.verify_payment(reference, user=request.user)
        return Response(payment_payload(payment, request))


@csrf_exempt
@require_POST
def paystack_webhook(request):
    """Paystack server-to-server notifications. Authenticated by HMAC signature."""
    signature = request.headers.get("x-paystack-signature", "")
    raw_body = request.body
    if not paystack.valid_signature(raw_body, signature):
        logger.warning("Rejected Paystack webhook with invalid signature")
        return HttpResponse(status=401)

    payload = services.parse_webhook_body(raw_body)
    if not isinstance(payload, dict):
        return HttpResponse(status=400)

    try:
        result = services.process_webhook(payload)
    except Exception:
        # 500 makes Paystack retry later; the event row was rolled back.
        logger.exception("Paystack webhook processing failed")
        return HttpResponse(status=500)

    logger.info("Paystack webhook %s: %s", payload.get("event"), result)
    return HttpResponse(status=200)


initialize_order_payment_view = InitializeOrderPaymentAPIView.as_view()
boost_plans_view = BoostPlansListAPIView.as_view()
initialize_boost_view = InitializeBoostAPIView.as_view()
my_boosts_view = MyBoostsListAPIView.as_view()
verify_payment_view = VerifyPaymentAPIView.as_view()

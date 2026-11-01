from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from NaijaBay.pagination import StandardPagination
from NaijaBay.throttling import CartThrottling, CheckoutThrottling, OrderThrottling
from . import services
from .models import Order, OrderItem
from .serializers import (
    CartSerializer,
    ItemStatusSerializer,
    OrderSerializer,
    SalesItemSerializer,
    ShippingSerializer,
)


def _cart_response(request, cart, code=status.HTTP_200_OK):
    return Response(CartSerializer(cart, context={"request": request}).data, status=code)


# =============================================================================
# CART
# =============================================================================

@extend_schema_view(
    get=extend_schema(tags=["Orders"], operation_id="View Cart"),
    delete=extend_schema(tags=["Orders"], operation_id="Clear Cart"),
)
class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [CartThrottling]
    serializer_class = CartSerializer

    def get(self, request):
        return _cart_response(request, services.get_cart(request.user))

    def delete(self, request):
        return _cart_response(request, services.clear_cart(request.user))


@extend_schema_view(post=extend_schema(tags=["Orders"], operation_id="Add To Cart"))
class CartAddAPIView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [CartThrottling]
    serializer_class = CartSerializer

    def post(self, request):
        cart = services.add_to_cart(
            request.user,
            request.data.get("product_id"),
            request.data.get("quantity", 1),
        )
        return _cart_response(request, cart, status.HTTP_201_CREATED)


@extend_schema_view(
    patch=extend_schema(tags=["Orders"], operation_id="Update Cart Quantity"),
    delete=extend_schema(tags=["Orders"], operation_id="Remove From Cart"),
)
class CartItemAPIView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [CartThrottling]
    serializer_class = CartSerializer

    def patch(self, request, product_id):
        cart = services.set_cart_quantity(
            request.user, product_id, request.data.get("quantity")
        )
        return _cart_response(request, cart)

    def delete(self, request, product_id):
        cart = services.remove_cart_item(request.user, product_id)
        return _cart_response(request, cart)


# =============================================================================
# CHECKOUT & ORDERS
# =============================================================================

@extend_schema_view(
    post=extend_schema(
        tags=["Orders"], operation_id="Checkout",
        request=ShippingSerializer, responses={201: OrderSerializer},
    )
)
class CheckoutAPIView(APIView):
    """Create (or reuse) an unpaid order from the cart. Pay it via
    ``/payments/orders/<reference>/initialize/``."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [CheckoutThrottling]
    serializer_class = ShippingSerializer

    def post(self, request):
        serializer = ShippingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = services.create_order_from_cart(request.user, serializer.validated_data)
        return Response(
            OrderSerializer(order, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(get=extend_schema(tags=["Orders"], operation_id="My Orders"))
class MyOrdersListAPIView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [OrderThrottling]
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = (
            Order.objects.filter(buyer=self.request.user)
            .prefetch_related("items", "items__product__images", "items__seller", "payments")
            .order_by("-created_at")
        )
        payment = (self.request.query_params.get("payment_status") or "").lower()
        if payment in {"paid", "unpaid"}:
            queryset = queryset.filter(payment_status=payment)
        return queryset


@extend_schema_view(get=extend_schema(tags=["Orders"], operation_id="Order Detail"))
class OrderDetailAPIView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [OrderThrottling]
    lookup_field = "reference"
    lookup_url_kwarg = "reference"

    def get_queryset(self):
        # Scoped to the buyer: other people's orders simply 404.
        return Order.objects.filter(buyer=self.request.user).prefetch_related(
            "items", "items__product__images", "items__seller", "payments"
        )


@extend_schema_view(post=extend_schema(tags=["Orders"], operation_id="Cancel Order"))
class CancelOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [OrderThrottling]
    serializer_class = OrderSerializer

    def post(self, request, reference):
        order = services.cancel_order(request.user, reference)
        return Response(OrderSerializer(order, context={"request": request}).data)


# =============================================================================
# SELLER SALES
# =============================================================================

@extend_schema_view(get=extend_schema(tags=["Orders"], operation_id="My Sales"))
class SalesListAPIView(ListAPIView):
    serializer_class = SalesItemSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [OrderThrottling]
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = (
            OrderItem.objects.filter(
                seller=self.request.user, order__payment_status="paid"
            )
            .select_related("order", "order__buyer")
            .prefetch_related("product__images")
            .order_by("-order__paid_at", "-id")
        )
        item_status = (self.request.query_params.get("status") or "").lower()
        if item_status in {"pending", "processing", "shipped", "delivered", "cancelled"}:
            queryset = queryset.filter(status=item_status)
        return queryset


@extend_schema_view(
    post=extend_schema(
        tags=["Orders"], operation_id="Update Sale Status",
        request=ItemStatusSerializer, responses={200: SalesItemSerializer},
    )
)
class SalesStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [OrderThrottling]
    serializer_class = ItemStatusSerializer

    def post(self, request, item_id):
        serializer = ItemStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = services.update_item_status(
            request.user, item_id, serializer.validated_data["status"]
        )
        item = (
            OrderItem.objects.select_related("order", "order__buyer")
            .prefetch_related("product__images")
            .get(pk=item.pk)
        )
        return Response(SalesItemSerializer(item, context={"request": request}).data)


cart_view = CartAPIView.as_view()
cart_add_view = CartAddAPIView.as_view()
cart_item_view = CartItemAPIView.as_view()
checkout_view = CheckoutAPIView.as_view()
my_orders_view = MyOrdersListAPIView.as_view()
order_detail_view = OrderDetailAPIView.as_view()
cancel_order_view = CancelOrderAPIView.as_view()
sales_list_view = SalesListAPIView.as_view()
sales_status_view = SalesStatusAPIView.as_view()

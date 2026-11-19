from django.urls import path
from .api_extra import (
    SafeDealListAPIView,
    SafeDealAcceptAPIView,
    SafeDealTrackingAPIView,
    SafeDealMarkDeliveredAPIView,
    SafeDealConfirmAPIView,
    SafeDealProblemAPIView,
    SafeDealExtendAPIView,
)
from .views import (
    cart_view,
    cart_add_view,
    cart_item_view,
    checkout_view,
    my_orders_view,
    order_detail_view,
    cancel_order_view,
    sales_list_view,
    sales_status_view,
)


urlpatterns = [
    path('cart/', cart_view, name='cart'),  # view (GET) / clear (DELETE) cart
    path('cart/items/', cart_add_view, name='cart-add'),  # add product to cart
    path('cart/items/<int:product_id>/', cart_item_view, name='cart-item'),  # update qty (PATCH) / remove (DELETE)
    path('checkout/', checkout_view, name='checkout'),  # create unpaid order from cart
    path('sales/', sales_list_view, name='sales-list'),  # seller's paid order items
    path('sales/<int:item_id>/status/', sales_status_view, name='sales-status'),  # seller updates fulfilment
    path('', my_orders_view, name='orders-list'),  # my orders
    # Safe Deal (escrow) — literal path must precede the <reference> catch-all
    path('safe-deal/', SafeDealListAPIView.as_view(), name='safe-deal-list'),
    path('<str:reference>/cancel/', cancel_order_view, name='order-cancel'),  # cancel unpaid order
    path('<str:reference>/', order_detail_view, name='order-detail'),  # order detail
    # Safe Deal actions
    path('<str:reference>/safe-deal/accept/', SafeDealAcceptAPIView.as_view(), name='safe-deal-accept'),
    path('<str:reference>/safe-deal/tracking/', SafeDealTrackingAPIView.as_view(), name='safe-deal-tracking'),
    path('<str:reference>/safe-deal/delivered/', SafeDealMarkDeliveredAPIView.as_view(), name='safe-deal-delivered'),
    path('<str:reference>/safe-deal/confirm/', SafeDealConfirmAPIView.as_view(), name='safe-deal-confirm'),
    path('<str:reference>/safe-deal/problem/', SafeDealProblemAPIView.as_view(), name='safe-deal-problem'),
    path('<str:reference>/safe-deal/extend/', SafeDealExtendAPIView.as_view(), name='safe-deal-extend'),
]

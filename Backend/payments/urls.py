from django.urls import path
from .views import (
    initialize_order_payment_view,
    boost_plans_view,
    initialize_boost_view,
    my_boosts_view,
    verify_payment_view,
    paystack_webhook,
)


urlpatterns = [
    path('orders/<str:reference>/initialize/', initialize_order_payment_view, name='initialize-order-payment'),  # start Paystack checkout for an order
    path('boost/plans/', boost_plans_view, name='boost-plans'),  # available boost plans
    path('boost/initialize/', initialize_boost_view, name='initialize-boost'),  # start Paystack checkout for a boost
    path('boost/my/', my_boosts_view, name='my-boosts'),  # my active / expired boosts
    path('verify/<str:reference>/', verify_payment_view, name='verify-payment'),  # verify with Paystack (callback page)
    path('webhook/', paystack_webhook, name='paystack-webhook'),  # Paystack -> server webhook
]

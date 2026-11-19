from django.urls import path
from .api_extra import (
    CreditAccountAPIView,
    CreditTransactionListAPIView,
    ReferralListAPIView,
    BoostAutoRenewalListCreateAPIView,
    BoostAutoRenewalDetailAPIView,
    ProSalesCampaignListCreateAPIView,
    ProSalesCampaignDetailAPIView,
)
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
    # Jiji-style monetisation extras
    path('credit/', CreditAccountAPIView.as_view(), name='credit-account'),
    path('credit/transactions/', CreditTransactionListAPIView.as_view(), name='credit-transactions'),
    path('referrals/', ReferralListAPIView.as_view(), name='referrals-list'),
    path('boost/auto-renew/', BoostAutoRenewalListCreateAPIView.as_view(), name='auto-renew-list'),
    path('boost/auto-renew/<int:pk>/', BoostAutoRenewalDetailAPIView.as_view(), name='auto-renew-detail'),
    path('pro-sales/', ProSalesCampaignListCreateAPIView.as_view(), name='pro-sales-list'),
    path('pro-sales/<int:pk>/', ProSalesCampaignDetailAPIView.as_view(), name='pro-sales-detail'),
]

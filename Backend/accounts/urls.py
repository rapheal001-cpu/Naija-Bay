from django.urls import path, include
from .views import (
    notification_view,
    other_user_profile_view,
    create_store_view,
    store_detail_view,
    store_list_view,
    verification_status_view,
    confirm_payment_view,
)

urlpatterns = [
    # -------------------------------------------------------------------------
    # Store & Notifications
    # -------------------------------------------------------------------------
    path("stores/", store_list_view, name="store list"),
    path("create-store/", create_store_view, name="create-store"),
    path("store-detail/<slug:store_slug>/", store_detail_view, name="store-detail"),
    path("notifications/", notification_view, name="notifications"),
    # -------------------------------------------------------------------------
    # Other User profile
    # -------------------------------------------------------------------------
    path("user/<int:pk>/", other_user_profile_view, name="other-user-profile"),
    # -------------------------------------------------------------------------
    # Verification
    # -------------------------------------------------------------------------
    path("verification/status/", verification_status_view, name="verification-status"),
    path("verification/confirm-payment/", confirm_payment_view, name="confirm-payment"),
    # -------------------------------------------------------------------------
    # Auth Kit
    # -------------------------------------------------------------------------
    path("", include("auth_kit.urls")),
]

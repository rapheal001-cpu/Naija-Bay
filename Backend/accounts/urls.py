from django.urls import path, include
from .views import (
    notification_view,
    other_user_profile_view,
)

urlpatterns = [
    path("notifications/", notification_view, name="notifications"),
    # -------------------------------------------------------------------------
    # Other User profile
    # -------------------------------------------------------------------------
    path("user/<int:pk>/", other_user_profile_view, name="other-user-profile"),
    # -------------------------------------------------------------------------
    # Auth Kit
    # -------------------------------------------------------------------------
    path("", include("auth_kit.urls")),
]

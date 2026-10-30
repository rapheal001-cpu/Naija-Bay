from django.urls import path, include
from .views import (
    notification_view,
    other_user_profile_view,
    create_store_view,
    store_detail_view,
    my_store_view,
    followers_list_view,
    following_list_view,
)

urlpatterns = [
    path("notifications/", notification_view, name="notifications"),
    # -------------------------------------------------------------------------
    # Other User profile
    # -------------------------------------------------------------------------
    path("user/<int:pk>/", other_user_profile_view, name="other-user-profile"),
    # -------------------------------------------------------------------------
    # Store
    # -------------------------------------------------------------------------
    path("create-store/", create_store_view, name="create-store"),
    path("my-store/", my_store_view, name="my-store"),
    path("store-detail/<slug:slug>/", store_detail_view, name="store-detail"),
    # -------------------------------------------------------------------------
    # Followers
    # -------------------------------------------------------------------------
    path("followers/<int:pk>/", followers_list_view, name="followers-list"),
    path("following/<int:pk>/", following_list_view, name="following-list"),
    # -------------------------------------------------------------------------
    # Auth Kit
    # -------------------------------------------------------------------------
    path("", include("auth_kit.urls")),
]

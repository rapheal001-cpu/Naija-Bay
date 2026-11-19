from django.urls import path, include
from .api_extra import (
    SellerFeedbackListAPIView,
    SellerFeedbackCreateAPIView,
    SellerFeedbackDetailAPIView,
    FeedbackAppealAPIView,
    FeedbackResponseAPIView,
    SavedSearchListCreateAPIView,
    SavedSearchDetailAPIView,
    VerificationRequestCreateAPIView,
    MyVerificationAPIView,
)
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
    path("user/<int:pk>/", other_user_profile_view, name="other-user-profile"),
    path("create-store/", create_store_view, name="create-store"),
    path("my-store/", my_store_view, name="my-store"),
    path("store-detail/<slug:slug>/", store_detail_view, name="store-detail"),
    path("followers/<int:pk>/", followers_list_view, name="followers-list"),
    path("following/<int:pk>/", following_list_view, name="following-list"),
    path("feedback/", SellerFeedbackListAPIView.as_view(), name="feedback-list"),
    path("feedback/create/", SellerFeedbackCreateAPIView.as_view(), name="feedback-create"),
    path("feedback/<int:pk>/", SellerFeedbackDetailAPIView.as_view(), name="feedback-detail"),
    path("feedback/<int:pk>/appeal/", FeedbackAppealAPIView.as_view(), name="feedback-appeal"),
    path("feedback/<int:pk>/respond/", FeedbackResponseAPIView.as_view(), name="feedback-respond"),
    path("saved-searches/", SavedSearchListCreateAPIView.as_view(), name="saved-search-list"),
    path("saved-searches/<int:pk>/", SavedSearchDetailAPIView.as_view(), name="saved-search-detail"),
    path("verification/submit/", VerificationRequestCreateAPIView.as_view(), name="verification-submit"),
    path("verification/me/", MyVerificationAPIView.as_view(), name="verification-me"),
    path("", include("auth_kit.urls")),
]

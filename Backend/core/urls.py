from django.urls import path
from .views import (
    mark_all_notifications_as_read_view,
    mark_notification_as_read_view,
    delete_all_notifications_view,
    delete_notification_view,
    toggle_favorite_product_view,
)

urlpatterns = [
    # Notifications
    path(
        "mark-all-notifications-as-read/",
        mark_all_notifications_as_read_view,
        name="mark-all-notifications-as-read",
    ),
    path(
        "delete-all-notifications/",
        delete_all_notifications_view,
        name="delete-all-notifications",
    ),
    path(
        "mark-notification-as-read/<int:notification_id>/",
        mark_notification_as_read_view,
        name="mark-notification-as-read",
    ),
    path(
        "delete-notification/<int:notification_id>/",
        delete_notification_view,
        name="delete-notification",
    ),
    # Favorites
    path(
        "toggle-favorite-product/<slug:product_slug>/",
        toggle_favorite_product_view,
        name="toggle-favorite-product",
    ),
]

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from accounts.models import Follow, Notifications, User
from accounts.serializers.serializers import NotificationSerializer
from accounts.serializers.store import FollowUserSerializer
from products.models import Product
from products.serializers import ProductSerializer
from NaijaBay.throttling import (
    MarkAllNotificationsReadThrottling,
    FavoriteToggleThrottling,
    FollowToggleThrottling,
)
from NaijaBay.permissions import IsOwnerOnly


# =============================================================================
# NOTIFICATIONS
# =============================================================================

@extend_schema_view(
    post=extend_schema(tags=["Notifications"], operation_id="Mark All Read")
)
class MarkAllNotificationsAsReadAPIView(APIView):
    serializer_class = NotificationSerializer
    throttle_classes = [MarkAllNotificationsReadThrottling]
    permission_classes = [IsOwnerOnly]

    def post(self, request, *args, **kwargs):
        Notifications.objects.filter(
            user=request.user, read=False
        ).update(read=True)

        return Response(
            {
                "detail": "All notifications marked as read."
            },
            status=status.HTTP_200_OK,
        )

mark_all_notifications_as_read_view = MarkAllNotificationsAsReadAPIView.as_view()


@extend_schema_view(
    delete=extend_schema(tags=["Notifications"], operation_id="Delete All")
)
class DeleteAllNotificationsAPIView(APIView):
    serializer_class = NotificationSerializer
    throttle_classes = [MarkAllNotificationsReadThrottling]
    permission_classes = [IsOwnerOnly]

    def delete(self, request, *args, **kwargs):
        Notifications.objects.filter(user=request.user).delete()

        return Response(
            {
                "detail": "All notifications deleted."
            },
            status=status.HTTP_200_OK,
        )

delete_all_notifications_view = DeleteAllNotificationsAPIView.as_view()


@extend_schema_view(
    post=extend_schema(tags=["Notifications"], operation_id="Mark One Read")
)
class MarkNotificationAsReadAPIView(APIView):
    serializer_class = NotificationSerializer
    throttle_classes = [MarkAllNotificationsReadThrottling]
    permission_classes = [IsOwnerOnly]

    def post(self, request, notification_id, *args, **kwargs):
        notification = get_object_or_404(
            Notifications, id=notification_id, user=request.user
        )

        if not notification.read:
            notification.read = True
            notification.save(update_fields=["read"])

        return Response(
            {"detail": "Notification marked as read."},
            status=status.HTTP_200_OK,
        )

mark_notification_as_read_view = MarkNotificationAsReadAPIView.as_view()


@extend_schema_view(
    delete=extend_schema(tags=["Notifications"], operation_id="Delete One Notification")
)
class DeleteNotificationAPIView(APIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsOwnerOnly]
    throttle_classes = [MarkAllNotificationsReadThrottling]

    def delete(self, request, notification_id, *args, **kwargs):
        notification = get_object_or_404(
            Notifications, id=notification_id, user=request.user
        )
        notification.delete()

        return Response(
            {"detail": "Notification deleted."},
            status=status.HTTP_200_OK,
        )

delete_notification_view = DeleteNotificationAPIView.as_view()


# =============================================================================
# FAVORITES
# =============================================================================

@extend_schema_view(post=extend_schema(tags=["Products"], operation_id="Toggle Favorite"))
class ToggleFavoriteProductAPIView(APIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [FavoriteToggleThrottling]

    def post(self, request, product_slug, *args, **kwargs):
        product = get_object_or_404(Product, product_slug=product_slug, active=True)

        # Efficient membership check
        is_favorite = product.favorites.filter(pk=request.user.pk).exists()

        if is_favorite:
            product.favorites.remove(request.user)
            favorited = False
        else:
            product.favorites.add(request.user)
            favorited = True

        return Response(
            {
                "detail": "Product favorite updated successfully.",
                "favorited": favorited,
                "favorites_count": product.favorites.count(),
            },
            status=status.HTTP_200_OK,
        )

toggle_favorite_product_view = ToggleFavoriteProductAPIView.as_view()


# =============================================================================
# FOLLOW
# =============================================================================

@extend_schema_view(post=extend_schema(tags=["User"], operation_id="Toggle Follow User"))
class ToggleFollowUserAPIView(APIView):
    serializer_class = FollowUserSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [FollowToggleThrottling]

    def post(self, request, user_id, *args, **kwargs):
        if str(request.user.id) == str(user_id):
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target = get_object_or_404(User, id=user_id, is_active=True)
        follow, created = Follow.objects.get_or_create(
            follower=request.user, following=target
        )

        if created:
            Notifications.objects.create(
                user=target,
                notification_type="new_follower",
                message=f"{request.user.username} started following you.",
            )
            following = True
        else:
            follow.delete()
            following = False

        return Response(
            {
                "detail": (
                    f"You are now following {target.username}."
                    if following
                    else f"You unfollowed {target.username}."
                ),
                "following": following,
                "followers_count": target.followers.count(),
            },
            status=status.HTTP_200_OK,
        )


toggle_follow_user_view = ToggleFollowUserAPIView.as_view()

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema_view, extend_schema
from auth_kit.views import (
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
    RegisterView,
    LoginView,
    UserView,
    VerifyEmailView,
    ResendEmailVerificationView,
)
from accounts.models import Notifications, Store, User
from .serializers import (
    FollowUserSerializer,
    StoreCreateSerializer,
    StoreDetailSerializer,
    StoreSerializer,
    CustomUserSerializer,
    NotificationSerializer,
)
from NaijaBay.throttling import (
    LogoutThrottling,
    PasswordChangeThrottling,
    PasswordResetConfirmThrottling,
    PasswordResetThrottling,
    RegisterThrottling,
    LoginThrottling,
    ResendEmailVerificationThrottling,
    StoreThrottling,
    UserDetailThrottling,
    UserThrottling,
    VerifyEmailThrottling,
)
from NaijaBay.queryset_helper import with_seller_context
from NaijaBay.pagination import StandardPagination
from NaijaBay.permissions import IsOwnerOnly


# =============================================================================
# AUTH VIEWS
# =============================================================================

@extend_schema_view(post=extend_schema(tags=["Auth"], operation_id="Register"))
class CustomRegisterView(RegisterView):
    throttle_classes = [RegisterThrottling]

    def get_response_data(self, user):
        data = super().get_response_data(user)
        data["detail"] = (
            "Account created successfully. Verification email has been sent."
        )
        return data


@extend_schema_view(post=extend_schema(tags=["Auth"], operation_id="Verify Email"))
class CustomVerifyEmailView(VerifyEmailView):
    throttle_classes = [VerifyEmailThrottling]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            return Response(
                {"detail": "Success! Your email is verified."},
                status=status.HTTP_200_OK,
            )
        return response


@extend_schema_view(post=extend_schema(tags=["Auth"], operation_id="Resend Email"))
class CustomResendEmailVerificationView(ResendEmailVerificationView):
    throttle_classes = [ResendEmailVerificationThrottling]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            return Response(
                {"detail": "Verification link has been sent to your email."},
                status=status.HTTP_200_OK,
            )
        return response


@extend_schema_view(post=extend_schema(tags=["Auth"], operation_id="Login"))
class CustomLoginView(LoginView):
    throttle_classes = [LoginThrottling]

    def create_response_with_cookies(self, serializer):
        response = super().create_response_with_cookies(serializer)
        data = serializer.data
        response.data = {
            "access_token": data["access"],
            "access_expiration": data["access_expiration"],
            "refresh_expiration": data["refresh_expiration"],
            "last_login": data["user"]["last_login"],
            "detail": "Login successful.",
        }
        return response


@extend_schema_view(post=extend_schema(tags=["Auth"], operation_id="Logout"))
class CustomLogoutView(LogoutView):
    throttle_classes = [LogoutThrottling]


@extend_schema_view(post=extend_schema(tags=["Auth"], operation_id="Password Change"))
class CustomPasswordChangeView(PasswordChangeView):
    throttle_classes = [PasswordChangeThrottling]


@extend_schema_view(post=extend_schema(tags=["Auth"], operation_id="Password Reset"))
class CustomPasswordResetView(PasswordResetView):
    throttle_classes = [PasswordResetThrottling]


@extend_schema_view(post=extend_schema(tags=["Auth"], operation_id="Password Reset Confirm"))
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    throttle_classes = [PasswordResetConfirmThrottling]


# =============================================================================
# CURRENT USER PROFILE (GET / PATCH)
# =============================================================================

@extend_schema_view(
    get=extend_schema(tags=["User"], operation_id="Current User Profile"),
    patch=extend_schema(tags=["User"], operation_id="Update Current User"),
    put=extend_schema(tags=["User"], operation_id="Replace Current User"),
)
class CustomUserView(UserView):
    serializer_class = CustomUserSerializer
    throttle_classes = [UserThrottling]

    def get_object(self):
        return User.objects.prefetch_related(
            'products',
            "products__images",
            'favorite_products',
            "favorite_products__images",
            "notifications",
        ).get(pk=self.request.user.pk)


# =============================================================================
# OTHER USER PROFILE
# =============================================================================

@extend_schema_view(get=extend_schema(tags=["User"], operation_id="Other User Profile"))
class OtherUserProfileAPIView(RetrieveAPIView):
    queryset = with_seller_context(User.objects.filter(is_active=True))
    serializer_class = CustomUserSerializer
    throttle_classes = [UserDetailThrottling]
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

other_user_profile_view = OtherUserProfileAPIView.as_view()


# =============================================================================
# NOTIFICATIONS
# =============================================================================

@extend_schema_view(get=extend_schema(tags=["User"], operation_id="User Notifications"))
class NotificationAPIView(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsOwnerOnly]
    throttle_classes = [UserThrottling]

    def get_queryset(self):
        return (
            Notifications.objects.filter(user=self.request.user)
            .select_related("user")
            .order_by("-timestamp")
        )

notification_view = NotificationAPIView.as_view()

# =============================================================================
# STORE
# =============================================================================

@extend_schema_view(
    post=extend_schema(
        tags=["Store"],
        operation_id="Create Or Update Store",
        request=StoreCreateSerializer,
        responses={200: StoreDetailSerializer, 201: StoreDetailSerializer},
    )
)
class StoreCreateAPIView(CreateAPIView):
    """Create the authenticated user's store, or update it when it exists."""

    serializer_class = StoreCreateSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [StoreThrottling]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, *args, **kwargs):
        instance = getattr(request.user, "store", None)
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        name_changed = bool(
            instance and "name" in serializer.validated_data
            and serializer.validated_data["name"] != instance.name
        )
        store = serializer.save(user=request.user)

        if name_changed:
            # Regenerate the slug so public URLs follow the new name.
            store.slug = ""
            store.save(update_fields=["slug"])

        output = StoreDetailSerializer(store, context={"request": request})
        return Response(
            output.data,
            status=status.HTTP_200_OK if instance else status.HTTP_201_CREATED,
        )


create_store_view = StoreCreateAPIView.as_view()


@extend_schema_view(
    get=extend_schema(tags=["Store"], operation_id="Store Detail"),
    put=extend_schema(
        tags=["Store"], operation_id="Replace Store", request=StoreCreateSerializer
    ),
    patch=extend_schema(
        tags=["Store"], operation_id="Update Store", request=StoreCreateSerializer
    ),
    delete=extend_schema(tags=["Store"], operation_id="Delete Store"),
)
class StoreDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Store.objects.select_related("user").all()
    serializer_class = StoreDetailSerializer
    lookup_field = "slug"
    throttle_classes = [StoreThrottling]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return StoreCreateSerializer
        return StoreDetailSerializer

    def perform_update(self, serializer):
        if serializer.instance.user_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You can only update your own store.")

        name_changed = "name" in serializer.validated_data
        store = serializer.save()
        if name_changed:
            store.slug = ""
            store.save(update_fields=["slug"])

    def perform_destroy(self, instance):
        if instance.user_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You can only delete your own store.")
        instance.delete()


store_detail_view = StoreDetailAPIView.as_view()


@extend_schema_view(get=extend_schema(tags=["Store"], operation_id="My Store"))
class MyStoreAPIView(RetrieveAPIView):
    serializer_class = StoreDetailSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [StoreThrottling]

    def get_object(self):
        store = getattr(self.request.user, "store", None)
        if not store:
            from rest_framework.exceptions import NotFound

            raise NotFound("You have not created a store yet.")
        return store


my_store_view = MyStoreAPIView.as_view()


# =============================================================================
# FOLLOWERS / FOLLOWING
# =============================================================================

class FollowersListAPIView(ListAPIView):
    serializer_class = FollowUserSerializer
    permission_classes = [AllowAny]
    throttle_classes = [UserDetailThrottling]
    pagination_class = StandardPagination

    def get_queryset(self):
        from accounts.models import Follow

        ids = Follow.objects.filter(following_id=self.kwargs["pk"]).values_list(
            "follower_id", flat=True
        )
        return User.objects.filter(id__in=ids, is_active=True).order_by("username")


followers_list_view = FollowersListAPIView.as_view()


class FollowingListAPIView(ListAPIView):
    serializer_class = FollowUserSerializer
    permission_classes = [AllowAny]
    throttle_classes = [UserDetailThrottling]
    pagination_class = StandardPagination

    def get_queryset(self):
        from accounts.models import Follow

        ids = Follow.objects.filter(follower_id=self.kwargs["pk"]).values_list(
            "following_id", flat=True
        )
        return User.objects.filter(id__in=ids, is_active=True).order_by("username")


following_list_view = FollowingListAPIView.as_view()

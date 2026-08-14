from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)
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
from accounts.models import Notifications, User
from accounts.serializers.serializers import NotificationSerializer
from accounts.serializers.user import (
    CustomUserSerializer,
)
from NaijaBay.throttling import (
    LogoutThrottling,
    PasswordChangeThrottling,
    PasswordResetConfirmThrottling,
    PasswordResetThrottling,
    RegisterThrottling,
    LoginThrottling,
    ResendEmailVerificationThrottling,
    UserDetailThrottling,
    UserThrottling,
    VerifyEmailThrottling,
)
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
    put=extend_schema(tags=["User"], operation_id="Update Current User"),
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
    queryset = User.objects.filter(is_active=True).prefetch_related("products", "products__images", "favorite_products", "favorite_products__images")
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
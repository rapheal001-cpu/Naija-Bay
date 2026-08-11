from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.generics import (
    get_object_or_404,
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.parsers import MultiPartParser, FormParser
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
from accounts.models import Notifications, User, Store, UserVerification
from accounts.serializers.serializers import NotificationSerializer, StoreSerializer
from accounts.serializers.user import (
    CustomUserSerializer,
    UserVerificationSerializer,
    UserVerificationPaymentSerializer,
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
from NaijaBay.permissions import IsOnlyVerifiedUser, IsStoreOwnerOrReadOnly, IsOwnerOnly

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
            "followers",
            "following",
            "notifications",
        ).get(pk=self.request.user.pk)


# =============================================================================
# OTHER USER PROFILE
# =============================================================================

@extend_schema_view(get=extend_schema(tags=["User"], operation_id="Other User Profile"))
class OtherUserProfileAPIView(RetrieveAPIView):
    queryset = User.objects.filter(is_active=True).prefetch_related("products", "products__images", "favorite_products", "favorite_products__images", "followers", "following")
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

@extend_schema_view(get=extend_schema(tags=['Store'], operation_id="Store List"))
class StoreListAPIView(ListAPIView):
    queryset = (
        Store.objects.select_related("store_user")
        .prefetch_related("store_members")
        .order_by("-created_at")
    )
    serializer_class = StoreSerializer
    permission_classes = [AllowAny]

store_list_view = StoreListAPIView.as_view()


@extend_schema_view(
    get=extend_schema(tags=["Store"], operation_id="Current Store Detail"),
    put=extend_schema(tags=["Store"], operation_id="Update Store Detail"),
    patch=extend_schema(tags=["Store"], operation_id="Partially Update Store Detail"),
    delete=extend_schema(tags=["Store"], operation_id="Delete Store"),
)
class StoreDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = StoreSerializer
    permission_classes = [IsStoreOwnerOrReadOnly | IsAdminUser]
    throttle_classes = [UserThrottling]
    lookup_field = 'store_slug'
    lookup_url_kwarg = 'store_slug'

store_detail_view = StoreDetailAPIView.as_view()


@extend_schema_view(post=extend_schema(tags=["Store"], operation_id="Create Store"))
class CreateStoreAPIView(CreateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsOnlyVerifiedUser | IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [UserThrottling]

    def perform_create(self, serializer):
        serializer.save(store_user=self.request.user)

create_store_view = CreateStoreAPIView.as_view()


# =============================================================================
# USER VERIFICATION (PAID BADGE)
# =============================================================================

@extend_schema_view(get=extend_schema(tags=["Verification"], operation_id="Verification Status"))
class UserVerificationStatusView(RetrieveAPIView):
    serializer_class = UserVerificationSerializer
    throttle_classes = [UserThrottling]

    def get_object(self):
        verification, _ = UserVerification.objects.get_or_create(user=self.request.user)

        return verification

verification_status_view = UserVerificationStatusView.as_view()


@extend_schema_view(post=extend_schema(tags=["Verification"], operation_id="Confirm Payment"))
class ConfirmVerificationPaymentView(APIView):
    serializer_class = UserVerification
    throttle_classes = [UserThrottling]

    def post(self, request, *args, **kwargs):
        verification = get_object_or_404(UserVerification, user=request.user)
        serializer = UserVerificationPaymentSerializer(
            verification,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "detail": "Payment confirmed. Your account is now verified.",
                "verified": verification.is_verified,
                "verified_at": verification.verified_at,
            },
            status=status.HTTP_200_OK,
        )

confirm_payment_view = ConfirmVerificationPaymentView.as_view()

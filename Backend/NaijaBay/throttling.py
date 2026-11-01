from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


# Registration Throttling
class RegisterThrottling(AnonRateThrottle):
    scope = 'register'


# Verify Email Throttling
class VerifyEmailThrottling(AnonRateThrottle):
    scope = 'verify_email'


# Resend Email Verification Throttling
class ResendEmailVerificationThrottling(AnonRateThrottle):
    scope = 'resend_email_verification'


# Login Throttling
class LoginThrottling(AnonRateThrottle):
    scope = 'login'


# Logout Throttling
class LogoutThrottling(UserRateThrottle):
    scope = 'logout'


# Password Change Throttling
class PasswordChangeThrottling(UserRateThrottle):
    scope = 'password_change'


# Password Reset Throttling
class PasswordResetThrottling(AnonRateThrottle):
    scope = 'password_reset'


# Password Reset Confirm Throttling
class PasswordResetConfirmThrottling(AnonRateThrottle):
    scope = 'password_reset_confirm'


# User profile and notifications throttling
class UserThrottling(UserRateThrottle):
    scope = 'user_profile'


class UserDetailThrottling(AnonRateThrottle):
    scope = 'user_detail'


class MarkAllNotificationsReadThrottling(UserRateThrottle):
    scope = 'mark_all_notifications_read'


# Product Throttling
class ProductThrottling(AnonRateThrottle):
    scope = 'product'


# Create Product Throttling
class CreateProductThrottling(UserRateThrottle):
    scope = 'create_product'


# Favorite toggle throttling
class FavoriteToggleThrottling(UserRateThrottle):
    scope = 'favorite_toggle'


# Follow toggle throttling
class FollowToggleThrottling(UserRateThrottle):
    scope = 'follow_toggle'


# Store write throttling
class StoreThrottling(UserRateThrottle):
    scope = 'store'


# Messaging throttling
class MessageThrottling(UserRateThrottle):
    scope = 'message'


class ConversationThrottling(UserRateThrottle):
    scope = 'conversation'


# Abuse report throttling
class ReportThrottling(UserRateThrottle):
    scope = 'report'


# Cart throttling
class CartThrottling(UserRateThrottle):
    scope = 'cart'


# Checkout / payment start throttling
class CheckoutThrottling(UserRateThrottle):
    scope = 'checkout'


# Orders (read + status updates) throttling
class OrderThrottling(UserRateThrottle):
    scope = 'order'


# Ad boosting throttling
class BoostThrottling(UserRateThrottle):
    scope = 'boost'


# Payment verification throttling
class PaymentVerifyThrottling(UserRateThrottle):
    scope = 'payment_verify'
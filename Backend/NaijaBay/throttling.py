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
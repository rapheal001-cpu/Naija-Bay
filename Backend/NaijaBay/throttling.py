from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class RegisterThrottling(AnonRateThrottle):
    scope = 'register'


class VerifyEmailThrottling(AnonRateThrottle):
    scope = 'verify_email'


class ResendEmailVerificationThrottling(AnonRateThrottle):
    scope = 'resend_email_verification'


class LoginThrottling(AnonRateThrottle):
    scope = 'login'


class LogoutThrottling(UserRateThrottle):
    scope = 'logout'


class PasswordChangeThrottling(UserRateThrottle):
    scope = 'password_change'


class PasswordResetThrottling(AnonRateThrottle):
    scope = 'password_reset'


class PasswordResetConfirmThrottling(AnonRateThrottle):
    scope = 'password_reset_confirm'


class UserThrottling(UserRateThrottle):
    scope = 'user_profile'


class UserDetailThrottling(AnonRateThrottle):
    scope = 'user_detail'


class MarkAllNotificationsReadThrottling(UserRateThrottle):
    scope = 'mark_all_notifications_read'


class ProductThrottling(AnonRateThrottle):
    scope = 'product'


class CreateProductThrottling(UserRateThrottle):
    scope = 'create_product'


class FavoriteToggleThrottling(UserRateThrottle):
    scope = 'favorite_toggle'


class FollowToggleThrottling(UserRateThrottle):
    scope = 'follow_toggle'


class StoreThrottling(UserRateThrottle):
    scope = 'store'


class MessageThrottling(UserRateThrottle):
    scope = 'message'


class ConversationThrottling(UserRateThrottle):
    scope = 'conversation'


class ReportThrottling(UserRateThrottle):
    scope = 'report'


class CartThrottling(UserRateThrottle):
    scope = 'cart'


class CheckoutThrottling(UserRateThrottle):
    scope = 'checkout'


class OrderThrottling(UserRateThrottle):
    scope = 'order'


class BoostThrottling(UserRateThrottle):
    scope = 'boost'


class PaymentVerifyThrottling(UserRateThrottle):
    scope = 'payment_verify'
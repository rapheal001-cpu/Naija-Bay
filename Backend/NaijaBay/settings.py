"""NaijaBay Django settings.

Organised in small sections with helpers so environment handling is consistent.
Behaviour matches the previous version: development defaults to SQLite, in-memory
cache/channels and local media; production switches each backend via env vars.
"""

from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse
import logging
import os

from decouple import config
from django.core.exceptions import ImproperlyConfigured


# =============================================================================
# Paths and environment helpers
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file(candidate: Path) -> bool:
    """Load KEY=VALUE pairs without overriding the real process environment."""
    if not candidate.exists():
        return False
    for line in candidate.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)
    return True


def _load_env_files():
    """Production loads .env.production only; development loads .env."""
    base = Path(__file__).resolve().parent.parent
    if os.environ.get("ENVIRONMENT") == "production":
        if _load_env_file(base / ".env.production"):
            return
    _load_env_file(base / ".env")


_load_env_files()


def _csv(name: str, default: str = "") -> list[str]:
    """Comma-separated environment value -> trimmed, non-empty list."""
    return [item.strip() for item in config(name, default=default, cast=str).split(",") if item.strip()]


def _hostnames(values: list[str]) -> list[str]:
    """Accept either bare hostnames or full URLs in ALLOWED_HOSTS."""
    hosts = []
    for value in values:
        hostname = urlparse(value).hostname or value
        if hostname and hostname not in hosts:
            hosts.append(hostname)
    return hosts


def _secret_key() -> str:
    value = config("SECRET_KEY", default="", cast=str)
    placeholders = ("django-insecure", "CHANGE_ME", "YOUR_")
    if IS_PRODUCTION and (not value or any(p in value for p in placeholders)):
        raise ImproperlyConfigured("SECRET_KEY must be set to a secure value in production.")
    return value or "django-insecure-dev-only-key-change-in-production"


# =============================================================================
# Runtime mode and security
# =============================================================================

ENVIRONMENT = config("ENVIRONMENT", default="development", cast=str)
IS_PRODUCTION = ENVIRONMENT == "production"

logger = logging.getLogger(__name__)

DEBUG = config("DEBUG", default=False, cast=bool)
if IS_PRODUCTION and DEBUG:
    raise ImproperlyConfigured("DEBUG must be False in production.")

SECRET_KEY = _secret_key()

ALLOWED_HOSTS = _hostnames(_csv("ALLOWED_HOSTS"))
if IS_PRODUCTION and not ALLOWED_HOSTS:
    raise ImproperlyConfigured("ALLOWED_HOSTS must be set in production.")
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"] if DEBUG else []

CSRF_TRUSTED_ORIGINS = _csv("CSRF_TRUSTED_ORIGINS")
if DEBUG and not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

if IS_PRODUCTION:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SAMESITE = "None"
    CSRF_COOKIE_SAMESITE = "None"
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"

AUTH_USER_MODEL = "accounts.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =============================================================================
# Apps and middleware
# =============================================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Local apps
    "accounts.apps.AccountsConfig",
    "products.apps.ProductsConfig",
    "core.apps.CoreConfig",
    "messaging.apps.MessagingConfig",
    "orders.apps.OrdersConfig",
    "payments.apps.PaymentsConfig",
    "NaijaBay",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "axes",
    "allauth",
    "allauth.account",
    "auth_kit",
    "drf_spectacular",
    "phonenumber_field",
    "django_filters",
    "cloudinary",
    "cloudinary_storage",
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "NaijaBay.middleware.SecurityHeadersMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "NaijaBay.middleware.OwnerOnlyDjangoAdminMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "NaijaBay.middleware.TrustedOriginMiddleware",
    "NaijaBay.middleware.CsrfGuardMiddleware",
    "axes.middleware.AxesMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

SITE_ID = config("SITE_ID", default=1, cast=int)


# =============================================================================
# CORS
# =============================================================================

CORS_ALLOWED_ORIGINS = _csv("CORS_ALLOWED_ORIGINS")
if DEBUG and not CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "x-csrftoken",
    "x-requested-with",
]


# =============================================================================
# URLs and templates
# =============================================================================

ROOT_URLCONF = "NaijaBay.urls"
ASGI_APPLICATION = "NaijaBay.asgi.application"
WSGI_APPLICATION = "NaijaBay.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
            ],
        },
    },
]


# =============================================================================
# Database
# =============================================================================

DATABASE_URL = config("DATABASE_URL", default=None)
if IS_PRODUCTION and DATABASE_URL and "CHANGE_ME" in DATABASE_URL:
    raise ImproperlyConfigured("DATABASE_URL contains placeholder values.")

if DATABASE_URL:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL, conn_max_age=600, conn_health_checks=True
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# =============================================================================
# Authentication and password rules
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = config("LANGUAGE_CODE", default="en-us", cast=str)
TIME_ZONE = config("TIME_ZONE", default="Africa/Lagos", cast=str)
USE_I18N = True
USE_TZ = True

SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
APPEND_SLASH = True


# =============================================================================
# Static files and media storage
# =============================================================================

STATIC_URL = "/static/"
STATICFILES_DIRS = (
    [os.path.join(BASE_DIR, "static")]
    if os.path.exists(os.path.join(BASE_DIR, "static"))
    else []
)
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

MEDIA_STORAGE_BACKEND = config(
    "MEDIA_STORAGE_BACKEND",
    cast=str,
    default="local" if ENVIRONMENT == "development" else "cloudinary",
)
MEDIA_STORAGE_BACKENDS = {
    "development": {"local", "cloudinary"},
    "production": {"s3", "cloudinary"},
    "staging": {"s3", "cloudinary"},
}
ALLOWED_MEDIA_STORAGES = MEDIA_STORAGE_BACKENDS.get(
    ENVIRONMENT, MEDIA_STORAGE_BACKENDS["production"]
)
if MEDIA_STORAGE_BACKEND not in ALLOWED_MEDIA_STORAGES:
    raise ImproperlyConfigured(
        f"MEDIA_STORAGE_BACKEND={MEDIA_STORAGE_BACKEND!r} is not allowed for "
        f"ENVIRONMENT={ENVIRONMENT!r}. Allowed: {sorted(ALLOWED_MEDIA_STORAGES)}."
    )

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", cast=str, default="")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", cast=str, default="")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", cast=str, default="")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", cast=str, default="us-east-1")
AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL", cast=str, default="")
AWS_S3_CUSTOM_DOMAIN = config("AWS_S3_CUSTOM_DOMAIN", cast=str, default="")

if MEDIA_STORAGE_BACKEND == "local":
    MEDIA_BACKEND = "django.core.files.storage.FileSystemStorage"
elif MEDIA_STORAGE_BACKEND == "s3":
    if not AWS_STORAGE_BUCKET_NAME:
        raise ImproperlyConfigured("AWS_STORAGE_BUCKET_NAME is required for S3 storage.")
    MEDIA_BACKEND = "NaijaBay.storage.S3MediaStorage"
else:  # cloudinary
    MEDIA_BACKEND = "NaijaBay.storage.AutoResourceCloudinaryStorage"
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": config("CLOUD_NAME", default=""),
        "API_KEY": config("CLOUD_API_KEY", default=""),
        "API_SECRET": config("CLOUD_API_SECRET", default=""),
    }

# Optional signed preset so Cloudinary can enforce a real file-size limit on
# browser-direct uploads (the API response field is only advisory).
CLOUDINARY_UPLOAD_PRESET = config("CLOUDINARY_UPLOAD_PRESET", default="", cast=str)

STORAGES = {
    "default": {"BACKEND": MEDIA_BACKEND},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}


# =============================================================================
# Django REST framework
# =============================================================================

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"]
    + (["rest_framework.renderers.BrowsableAPIRenderer"] if DEBUG else []),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "auth_kit.authentication.JWTCookieAuthentication"
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_THROTTLE_RATES": {
        "register": "1000/day",
        "verify_email": "1000/day",
        "resend_email_verification": "1000/day",
        "login": "100/day",
        "logout": "1000/day",
        "password_change": "1000/day",
        "password_reset": "1000/day",
        "password_reset_confirm": "1000/day",
        "user_profile": "1000/day",
        "user_detail": "1000/hour",
        "mark_all_notifications_read": "1000/day",
        "product": "100/hour",
        "create_product": "100/day",
        "favorite_toggle": "500/hour",
        "follow_toggle": "500/hour",
        "store": "100/day",
        "message": "1000/hour",
        "conversation": "300/hour",
        "report": "50/day",
        "cart": "2000/day",
        "checkout": "200/day",
        "order": "2000/day",
        "boost": "200/day",
        "payment_verify": "1000/day",
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "NaijaBay API",
    "DESCRIPTION": "NaijaBay Marketplace API — accounts, products, orders and payments.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/v1",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SERVE_AUTHENTICATION": ["auth_kit.authentication.JWTCookieAuthentication"],
    "CONTACT": {
        "name": "NaijaBay Support",
        "email": config("DEFAULT_FROM_EMAIL", default="support@naijabay.local", cast=str),
    },
    "LICENSE": {"name": "Proprietary"},
    "TAGS": [
        {"name": "Authentication", "description": "Register, login, password and verification."},
        {"name": "User", "description": "Profile, notifications and social endpoints."},
        {"name": "Products", "description": "Products, categories and attributes."},
        {"name": "Store", "description": "Store creation and management."},
        {"name": "Core", "description": "Favorites, follows and utilities."},
        {"name": "Messaging", "description": "Buyer and seller conversations."},
        {"name": "Feedback", "description": "Seller feedback and appeals."},
        {"name": "Safe Deal", "description": "Escrow-style order lifecycle."},
        {"name": "Verification", "description": "Verified ID (KYC) endpoints."},
        {"name": "Documentation", "description": "Swagger and ReDoc."},
    ],
    "SWAGGER_UI_SETTINGS": {
        "defaultModelsExpandDepth": -1,
        "docExpansion": "none",
        "persistAuthorization": True,
        "deepLinking": True,
        "withCredentials": True,
    },
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "cookieAuth": {"type": "apiKey", "in": "cookie", "name": "access"}
        }
    },
    "SECURITY": [{"cookieAuth": []}],
    "COMPONENT_SPLIT_REQUEST": True,
}


# =============================================================================
# JWT cookies, allauth and auth_kit
# =============================================================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=config("JWT_ACCESS_TOKEN_LIFETIME", default=15, cast=int)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=config("JWT_REFRESH_TOKEN_LIFETIME", default=1, cast=int)
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
}

ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_LOGIN_METHODS = {"email"}

AUTH_KIT = {
    "AUTH_TYPE": "jwt",
    "USE_AUTH_COOKIE": True,
    "AUTH_COOKIE_SECURE": IS_PRODUCTION,
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_SAMESITE": "None" if IS_PRODUCTION else "Lax",
    "AUTH_JWT_COOKIE_NAME": "access",
    "AUTH_JWT_REFRESH_COOKIE_NAME": "refresh",
    # Registration
    "REGISTER_SERIALIZER": "accounts.serializers.registration.CustomRegisterSerializer",
    "REGISTER_VIEW": "accounts.views.CustomRegisterView",
    "VERIFY_EMAIL_VIEW": "accounts.views.CustomVerifyEmailView",
    "RESEND_EMAIL_VERIFICATION_VIEW": "accounts.views.CustomResendEmailVerificationView",
    "FRONTEND_BASE_URL": None,
    "REGISTER_EMAIL_CONFIRM_PATH": None,
    "GET_EMAIL_VERIFICATION_URL_FUNC": "auth_kit.views.registration.get_email_verification_url",
    "SEND_VERIFY_EMAIL_FUNC": "auth_kit.views.registration.send_verify_email",
    "POST_SIGNUP_FUNC": "auth_kit.views.registration.default_post_signup",
    # Login / logout
    "LOGIN_REQUEST_SERIALIZER": "auth_kit.serializers.login_factors.LoginRequestSerializer",
    "LOGIN_RESPONSE_SERIALIZER": "auth_kit.serializers.login_factors.BaseLoginResponseSerializer",
    "LOGIN_SERIALIZER_FACTORY": "auth_kit.serializers.login.get_login_serializer",
    "LOGIN_VIEW": "accounts.views.CustomLoginView",
    "LOGOUT_SERIALIZER": "auth_kit.serializers.logout.AuthKitLogoutSerializer",
    "LOGOUT_VIEW": "accounts.views.CustomLogoutView",
    # User
    "USER_SERIALIZER": "accounts.serializers.user.CustomUserSerializer",
    "USER_VIEW": "accounts.views.CustomUserView",
    # Password
    "PASSWORD_CHANGE_SERIALIZER": "auth_kit.serializers.PasswordChangeSerializer",
    "PASSWORD_CHANGE_VIEW": "accounts.views.CustomPasswordChangeView",
    "PASSWORD_RESET_SERIALIZER": "auth_kit.serializers.PasswordResetSerializer",
    "PASSWORD_RESET_VIEW": "accounts.views.CustomPasswordResetView",
    "PASSWORD_RESET_CONFIRM_SERIALIZER": "auth_kit.serializers.PasswordResetConfirmSerializer",
    "PASSWORD_RESET_CONFIRM_VIEW": "accounts.views.CustomPasswordResetConfirmView",
    "PASSWORD_RESET_CONFIRM_PATH": None,
    "PASSWORD_RESET_URL_GENERATOR": "auth_kit.forms.password_reset_url_generator",
    "SEND_PASSWORD_RESET_EMAIL_FUNC": "auth_kit.forms.send_password_reset_email",
    "OLD_PASSWORD_FIELD_ENABLED": True,
    "PASSWORD_RESET_PREVENT_ENUMERATION": True,
    # JWT
    "JWT_TOKEN_CLAIMS_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "JWT_REFRESH_VIEW": "auth_kit.views.jwt.RefreshViewWithCookieSupport",
}

# Login brute-force lockout (time-based cool-off, not a permanent ban).
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_LOCK_OUT_AT_FAILURE = False
AXES_COOLOFF_MODE = "immediately"


# =============================================================================
# Email, phone and payments
# =============================================================================

EMAIL_HOST = config("EMAIL_HOST", default="", cast=str)
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="", cast=str)
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="", cast=str)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@naijabay.com", cast=str)

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if IS_PRODUCTION and EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
    else "django.core.mail.backends.console.EmailBackend"
)

PHONENUMBER_DEFAULT_REGION = "NG"

# Empty in development -> simulated checkout. Required in production.
PAYSTACK_SECRET_KEY = config("PAYSTACK_SECRET_KEY", default="", cast=str).strip()
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:5173", cast=str).strip()
DELIVERY_FEE = config("DELIVERY_FEE", default=0, cast=int)
if IS_PRODUCTION and not PAYSTACK_SECRET_KEY:
    raise ImproperlyConfigured("PAYSTACK_SECRET_KEY must be set in production.")


# =============================================================================
# Logging
# =============================================================================

LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {"format": "{levelname} {asctime} {message}", "style": "{"},
    },
    "filters": {
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOGS_DIR, "naijabay.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "filters": ["require_debug_false"],
        },
    },
    "loggers": {
        name: {"handlers": ["console", "file"], "level": "INFO", "propagate": False}
        for name in (
            "django", "products", "accounts", "chat", "orders", "payments", "messaging"
        )
    },
}


# =============================================================================
# Cache and Channels
# =============================================================================

REDIS_URL = config("REDIS_URL", cast=str, default="redis://127.0.0.1:6379/0")

if IS_PRODUCTION:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "SOCKET_CONNECT_TIMEOUT": 3,
                "SOCKET_TIMEOUT": 5,
            },
            "KEY_PREFIX": "naijabay",
            "TIMEOUT": 60 * 30,
        }
    }
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [
                    {
                        "address": REDIS_URL,
                        "socket_connect_timeout": 5,
                        "socket_timeout": 20,
                        "socket_keepalive": True,
                        "health_check_interval": 25,
                    }
                ],
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "naijabay-cache",
        }
    }
    CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
    }

import os
import logging
from pathlib import Path
from urllib.parse import urlparse
from decouple import config
from datetime import timedelta
import cloudinary

# =============================================================================
# ENVIRONMENT
# =============================================================================

ENVIRONMENT = config("ENVIRONMENT", default="development", cast=str)
IS_PRODUCTION = ENVIRONMENT == "production"

logger = logging.getLogger(__name__)


# =============================================================================
# PATHS
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# SECURITY
# =============================================================================

try:
    SECRET_KEY = config("SECRET_KEY", cast=str)
    if not SECRET_KEY or SECRET_KEY.startswith("django-insecure"):
        if IS_PRODUCTION:
            raise ValueError("SECRET_KEY must be set to a secure value in production.")
except Exception as e:
    if IS_PRODUCTION:
        raise e
    SECRET_KEY = "django-insecure-dev-only-key-change-in-production"

DEBUG = config("DEBUG", default=False, cast=bool)
if IS_PRODUCTION and DEBUG:
    raise ValueError("DEBUG must be False in production.")

# ALLOWED_HOSTS — robust parsing of URLs or plain hostnames
try:
    hosts_raw = config("ALLOWED_HOSTS", default="", cast=str)
    ALLOWED_HOSTS = []
    for host in hosts_raw.split(","):
        host = host.strip()
        if not host:
            continue
        parsed = urlparse(host)
        hostname = parsed.hostname or host
        if hostname:
            ALLOWED_HOSTS.append(hostname)

    if IS_PRODUCTION and not ALLOWED_HOSTS:
        raise ValueError("ALLOWED_HOSTS must be set in production.")
except Exception as e:
    if IS_PRODUCTION:
        raise e
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"] if DEBUG else []

AUTH_USER_MODEL = "accounts.User"

# CSRF
CSRF_TRUSTED_ORIGINS = []
if DEBUG:
    debug_csrf = config("CSRF_TRUSTED_ORIGINS", default="", cast=str)
    if debug_csrf:
        CSRF_TRUSTED_ORIGINS = [o.strip() for o in debug_csrf.split(",") if o.strip()]
    else:
        CSRF_TRUSTED_ORIGINS = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
else:
    CSRF_TRUSTED_ORIGINS = [
        o.strip()
        for o in config("CSRF_TRUSTED_ORIGINS", default="", cast=str).split(",")
        if o.strip()
    ]

# Production security headers
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


# =============================================================================
# APPS
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
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "allauth",
    "allauth.account",
    "auth_kit",
    "drf_spectacular",
    "phonenumber_field",
    "django_filters",
    "cloudinary",
    "cloudinary_storage",
]

SITE_ID = config("SITE_ID", default=1, cast=int)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


# =============================================================================
# MIDDLEWARE
# =============================================================================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =============================================================================
# CORS
# =============================================================================

CORS_ALLOWED_ORIGINS = []
if DEBUG:
    debug_cors = config("CORS_ALLOWED_ORIGINS", default="", cast=str)
    if debug_cors:
        CORS_ALLOWED_ORIGINS = [o.strip() for o in debug_cors.split(",") if o.strip()]
    else:
        CORS_ALLOWED_ORIGINS = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
else:
    CORS_ALLOWED_ORIGINS = [
        o.strip()
        for o in config("CORS_ALLOWED_ORIGINS", default="", cast=str).split(",")
        if o.strip()
    ]

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
# URLS & TEMPLATES
# =============================================================================

ROOT_URLCONF = "NaijaBay.urls"

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

WSGI_APPLICATION = "NaijaBay.wsgi.application"


# =============================================================================
# DATABASE
# =============================================================================

DATABASE_URL = config("DATABASE_URL", default=None)

if DATABASE_URL:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
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
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = config("LANGUAGE_CODE", default="en-us", cast=str)
TIME_ZONE = config("TIME_ZONE", default="Africa/Lagos", cast=str)
USE_I18N = True
USE_TZ = True


# =============================================================================
# STATIC & MEDIA
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

if IS_PRODUCTION:
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": config("CLOUD_NAME"),
        "API_KEY": config("CLOUD_API_KEY"),
        "API_SECRET": config("CLOUD_API_SECRET"),
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }


# =============================================================================
# REST FRAMEWORK
# =============================================================================

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ]
    + (["rest_framework.renderers.BrowsableAPIRenderer"] if DEBUG else []),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "auth_kit.authentication.JWTCookieAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
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
    },
}


# =============================================================================
# DRF SPECTACULAR
# =============================================================================

SPECTACULAR_SETTINGS = {
    "TITLE": "NaijaBay API",
    "DESCRIPTION": "NaijaBay Marketplace API — endpoints for accounts, products, chat, and verification.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/v1",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SERVE_AUTHENTICATION": ["auth_kit.authentication.JWTCookieAuthentication"],
    "CONTACT": {
        "name": "NaijaBay Support",
        "email": config(
            "DEFAULT_FROM_EMAIL", default="support@naijabay.local", cast=str
        ),
    },
    "LICENSE": {"name": "Proprietary"},
    "TAGS": [
        {
            "name": "Authentication",
            "description": "Register, login, password and verification endpoints.",
        },
        {
            "name": "User",
            "description": "Profile, notifications, and social endpoints.",
        },
        {
            "name": "Products",
            "description": "Product and category management endpoints.",
        },
        {"name": "Store", "description": "Store creation and management endpoints."},
        {"name": "Core", "description": "Favorites, follows, and utility endpoints."},
        {"name": "Chat", "description": "Chat message endpoints."},
        {"name": "Verification", "description": "Paid user verification endpoints."},
        {
            "name": "Documentation",
            "description": "Schema and interactive docs (Swagger / ReDoc).",
        },
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
            "cookieAuth": {
                "type": "apiKey",
                "in": "cookie",
                "name": "access",
            }
        }
    },
    "SECURITY": [{"cookieAuth": []}],
    "COMPONENT_SPLIT_REQUEST": True,
}


# =============================================================================
# SIMPLE JWT
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


# =============================================================================
# ALLAUTH
# =============================================================================

ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_LOGIN_METHODS = {"email"}


# =============================================================================
# AUTH KIT
# =============================================================================

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
    # Login / Logout
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


# =============================================================================
# EMAIL
# =============================================================================

EMAIL_HOST = config("EMAIL_HOST", default="", cast=str)
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="", cast=str)
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="", cast=str)
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL", default="noreply@naijabay.com", cast=str
)
EMAIL_TIMEOUT = 10

if IS_PRODUCTION and EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# =============================================================================
# PHONE NUMBER
# =============================================================================

PHONENUMBER_DEFAULT_REGION = "NG"


# =============================================================================
# LOGGING
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
        "simple": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
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
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "products": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "accounts": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "chat": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


# =============================================================================
# MISC
# =============================================================================

APPEND_SLASH = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "naijabay-cache",
    }
}

SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

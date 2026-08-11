# NaijaBay Backend API

NaijaBay is a Django REST Framework marketplace backend for Nigerian classifieds and local buying/selling flows. The backend currently powers authentication, profile management, product discovery, product creation, image uploads, favorites, notifications, and the shared API surface used by the frontend.

## What the backend does

The current API supports:

- user registration, login, logout, verification, password reset, and password change
- authenticated profile fetch and profile update flows
- public and authenticated user lookup routes
- product listing, category browsing, product detail retrieval, and user-specific product listing views
- product creation and image upload handling
- favorite toggling for products
- notification retrieval and mark-as-read workflows
- OpenAPI/schema generation and interactive docs through drf-spectacular
- chat-related app scaffolding alongside the marketplace and account modules

## Technology stack

- Python 3.x
- Django 6.x
- Django REST Framework
- auth_kit for cookie-based JWT authentication flow
- drf-spectacular for schema and docs
- SimpleJWT / cookie-auth integration for sessionless auth
- Django Allauth for account integration
- Django CORS Headers for frontend cross-origin support
- Pillow for image validation and upload handling
- python-decouple for environment-based config
- SQLite by default for local development, with optional PostgreSQL via `DATABASE_URL`

## Current backend architecture

```text
Backend/
├── NaijaBay/
│   ├── settings.py
│   ├── urls.py
│   ├── throttling.py
│   └── utils.py
├── accounts/
│   ├── models.py
│   ├── serializers/
│   ├── urls.py
│   └── views.py
├── chat/
│   └── ...
├── core/
│   └── models.py
├── products/
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── manage.py
├── requirements.txt
├── .env
└── db.sqlite3
```

## Runtime entry points

The Django project starts from:

```bash
cd Backend
py manage.py runserver 0.0.0.0:8000
```

The API is exposed at:

- `http://127.0.0.1:8000/api/v1/`
- `http://127.0.0.1:8000/api/v1/docs/`
- `http://127.0.0.1:8000/api/v1/redoc/`

If you are testing through a public tunnel, the same backend can also be reached through your Ngrok URL, provided the backend env settings and CORS/CSRF origins are updated to match it.

## API surface in the current implementation

### Auth and account routes (`/api/v1/accounts/auth/`)

These routes are routed through the auth_kit integration and cover the normal authentication lifecycle:

- `POST /api/v1/accounts/auth/register/`
- `POST /api/v1/accounts/auth/login/`
- `POST /api/v1/accounts/auth/logout/`
- `POST /api/v1/accounts/auth/verify-email/`
- `POST /api/v1/accounts/auth/resend-verify-email/`
- `POST /api/v1/accounts/auth/password-change/`
- `POST /api/v1/accounts/auth/password-reset/`
- `POST /api/v1/accounts/auth/password-reset-confirm/`
- `GET /api/v1/accounts/auth/user/`
- `PUT /api/v1/accounts/auth/user/`
- `GET /api/v1/accounts/auth/user/<id>/`
- `GET /api/v1/accounts/auth/notifications/`
- `POST /api/v1/core/mark-all-notifications-as-read/`

### Product routes (`/api/v1/products/`)

- `GET /api/v1/products/`
- `GET /api/v1/products/categories/`
- `POST /api/v1/products/create/`
- `POST /api/v1/products/create/images/`
- `GET /api/v1/products/user/`
- `GET /api/v1/products/detail/<slug>/`
- `POST /api/v1/core/toggle-favorite-product/<slug>/`

### Documentation routes

- `GET /api/v1/schema/`
- `GET /api/v1/docs/`
- `GET /api/v1/redoc/`

## Security and rate limiting

The project uses DRF throttling to protect public and authenticated endpoints. The active scopes are defined centrally in the Django settings and include:

- register
- verify_email
- resend_email_verification
- login
- logout
- password_change
- password_reset
- password_reset_confirm
- user_profile
- user_detail
- mark_all_notifications_read
- product
- create_product
- favorite_toggle

## Environment configuration

The backend uses a `.env` file for runtime configuration. A typical development configuration looks like this:

```env
ENVIRONMENT=development
SECRET_KEY=django-insecure-dev-only-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,your-ngrok-host
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://your-ngrok-host
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://your-ngrok-host
SITE_ID=1
TIME_ZONE=Africa/Lagos
LANGUAGE_CODE=en-us
DATABASE_URL=
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=1
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=noreply@naijabay.ng
```

Use `DATABASE_URL` for PostgreSQL in production. If it is omitted, the backend falls back to the local SQLite database.

## Local development workflow

1. Activate the virtual environment.
2. Install dependencies from `requirements.txt`.
3. Review and validate the `.env` file.
4. Run migrations.
5. Start the Django development server.
6. Use the docs routes and frontend flows to exercise the API.

## Recommended commands

```bash
cd Backend
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
py manage.py migrate
py manage.py check
py manage.py runserver 0.0.0.0:8000
```

## Notes for contributors

- Keep permissions and throttling decisions in the view layer.
- Keep serializers focused on validation and response shaping.
- Keep the frontend host configured through the browser-facing `.env` file rather than hardcoding hostnames in the UI.
- If you add or rename API routes, keep the frontend service layer in sync.
- Restart the Django process after changing `.env` values because the settings are loaded at startup.

## Project status

The backend is the API runtime for the NaijaBay marketplace and is currently aligned with the frontend’s auth, profile, notification, product, and discovery flows.

# NaijaBay Backend Development Guide

This document is the development-oriented guide for the current Django backend. It reflects the live API structure and the frontend integration model used by the project today.

## Project goal

The backend provides the trusted, authenticated API surface that the NaijaBay frontend consumes. It is built around account workflows, product data, user profile data, notifications, marketplace media uploads, and the shared chat application layer.

## Current development environment

- Python runtime: use the project virtual environment in `Backend/venv`
- Django settings module: `NaijaBay.settings`
- Default database: SQLite for local development
- Frontend host expectation: `http://localhost:5173` during local Vite development
- Public tunnel support: Ngrok-friendly configuration is supported when the backend `.env` contains the matching host/origin values
- API base path: `/api/v1/`

## Recommended local setup

### 1. Create the environment

```powershell
cd C:\Users\HP\OneDrive\Desktop\Projects\NaijaBay\Backend
py -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install packages

```bash
pip install -r requirements.txt
```

### 3. Confirm the `.env` file

The backend ships with a `.env` file in the project root. For development, ensure the values below are present and that the `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `CORS_ALLOWED_ORIGINS` entries match the frontend origin you are actually using:

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
```

### 4. Apply migrations

```bash
py manage.py migrate
```

### 5. Start the development server

```bash
py manage.py runserver 0.0.0.0:8000
```

## Important runtime notes

### API authentication model

The project is using the auth_kit authentication flow with cookie-based JWT integration. The client must be able to send and receive cookies from the API host for the session to behave correctly.

### Frontend integration contract

The frontend currently depends on these backend paths:

- `POST /api/v1/accounts/auth/login/`
- `POST /api/v1/accounts/auth/registration/`
- `GET /api/v1/accounts/auth/user/`
- `PUT /api/v1/accounts/auth/user/`
- `POST /api/v1/accounts/auth/password-reset/`
- `GET /api/v1/products/`
- `GET /api/v1/products/categories/`
- `POST /api/v1/products/create/`
- `POST /api/v1/products/create/images/`
- `GET /api/v1/products/detail/<slug>/`
- `POST /api/v1/core/toggle-favorite-product/<slug>/`
- `GET /api/v1/accounts/auth/notifications/`
- `POST /api/v1/core/mark-all-notifications-as-read/`

### Throttling configuration

All request-rate limits are centralized in the Django REST Framework settings and implemented through the project’s `NaijaBay/throttling.py` module. Current throttle scopes include:

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

## App layout

### `accounts/`

Contains custom user model management, notifications, account serializers, account views, and auth URL registration.

### `products/`

Contains product models, serializer validation, product URL routing, and marketplace views.

### `core/`

Contains shared category/state/city models used by the product listing system.

### `chat/`

Contains the chat application module and its routing/views for message-related flows.

### `NaijaBay/`

Contains the main Django config, settings, REST framework configuration, and project-wide throttling and utility definitions.

## Troubleshooting checklist

If the backend does not start correctly, verify the following:

- the virtual environment is active
- `requirements.txt` has been installed
- `.env` has valid values for `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and CORS/CSRF host origins
- the `DATABASE_URL` setting is empty for the default SQLite path, or is properly set for PostgreSQL
- the frontend is pointed at the correct backend origin and the backend has been restarted after `.env` changes
- the browser is not hitting a stale host or a mismatched Ngrok URL

## Production-oriented notes

For production, the service should be moved to a proper environment where:

- `DEBUG=False`
- `ENVIRONMENT=production`
- secure `SECRET_KEY` and `ALLOWED_HOSTS` are provided
- CORS and CSRF origins are pinned to the deployed frontend domain(s)
- a managed database is used instead of SQLite
- static/media storage is configured and served correctly by a reverse proxy

## Useful commands

```bash
py manage.py makemigrations
py manage.py migrate
py manage.py createsuperuser
py manage.py collectstatic --noinput
py manage.py test
py manage.py runserver 0.0.0.0:8000
```

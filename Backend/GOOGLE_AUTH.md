# Social Login (Google / Facebook / Apple / Truecaller) — Status & Setup

## Current status in Naija-Bay

**Not implemented.** Naija-Bay uses email + password registration with
mandatory email verification, and cookie-JWT sessions via `auth_kit` (`access`
and `refresh` HttpOnly cookies). `django-allauth` is installed, but only
`allauth` and `allauth.account` are in `INSTALLED_APPS` — there is no
`allauth.socialaccount` provider configured and no social-login endpoint.

Jiji supports Google, Facebook, Apple and Truecaller sign-in. Adding those
providers was deliberately deferred because it requires provider app
credentials (client IDs/secrets) that only the project owner can create. This
document records exactly what is needed so it can be enabled without guesswork.

## What must be added

### 1. Backend dependencies and settings

Allauth social support is already in `requirements.txt` (`django-allauth`).
Add to `INSTALLED_APPS` in `NaijaBay/settings.py`:

```python
"allauth.socialaccount",
"allauth.socialaccount.providers.google",
# plus facebook / apple when their credentials exist
```

Relevant settings to add (with env-backed values):

```python
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_QUERY_EMAIL = True
```

Truecaller is not a standard allauth provider; it needs a custom verification
flow (phone number confirmed via Truecaller's API) before linking an account.

### 2. Environment variables

Backend `.env` (secrets — never in frontend):

```env
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
SOCIAL_LOGIN_CALLBACK_BASE_URL=
```

Frontend `Frontend/Web/.env` (the client ID is publishable):

```env
VITE_GOOGLE_CLIENT_ID=
```

### 3. Endpoints

A minimal AuthKit-style social endpoint is needed, e.g.:

```
POST /api/v1/accounts/auth/social/google/   {"code": "..."}
POST /api/v1/accounts/auth/social/google/connect/   (authenticated) {"code": "..."}
```

The backend exchanges the short-lived code server-side and establishes the
**same** cookie session as password login (`access`/`refresh`). Tokens must
never be returned in JSON or stored in `localStorage`/`sessionStorage`.

### 4. Account-linking rules

- Only link an existing account when the provider email is **verified**.
- Never overwrite an existing user's email, role or privileges.
- New users get an email marked verified (provider already verified ownership)
  and still need a phone number for chat/contact features.
- Hide provider error details in responses (`SOCIAL_HIDE_AUTH_ERROR_DETAILS=True`).

### 5. Provider console setup (Google example)

1. Create a Google Cloud project and configure the OAuth consent screen
   (scopes `openid`, `email`, `profile`).
2. Create an OAuth client ID for a Web application.
3. Authorized JavaScript origin: `http://localhost:5173` (and the production web origin).
4. Authorized redirect URI: the backend callback, e.g.
   `http://localhost:8000/api/v1/accounts/auth/social/google/` (and the production
   equivalent, with a trailing slash).
5. Put the IDs in the env files above and run
   `python manage.py migrate socialaccount account`.

### 6. Frontend work

- Add a "Continue with Google" button on `SignIn` / `Register` using Google
  Identity Services to obtain a code, then POST it to the endpoint above.
- Add a "Connect Google" action in profile settings.
- Show a friendly "use social login" callout when password login is attempted
  on an account that has no usable password.

## Verification checklist once implemented

- New user via Google → cookies set, email verified, profile usable.
- Existing email + verified Google email → linked, no data overwritten.
- Existing email + unverified Google email → rejected.
- Invalid/expired/reused code → generic `400`.
- Password login on a Google-only account → clear sign-in guidance.
- `npm run build` and `manage.py test accounts` still pass.

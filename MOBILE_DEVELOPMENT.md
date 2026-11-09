# NaijaBay — Mobile Development Guide

> **Status:** Web-first. The backend API is ready for the future React Native
> app, but **no mobile client work has started** and none is implied.
> This guide records what the API gives mobile today, what mobile needs, and
> the decisions to make before writing code.

## 1. Authentication on mobile (cookie JWT — already there)

The backend authenticates with **HttpOnly cookies** (`access` / `refresh`,
SimpleJWT behind DRF Auth Kit). That is the *current* architecture:

- Web (browser) sends/receives cookies automatically.
- **React Native has no cookie jar by default**, but both major HTTP helpers
  support one: `axios` with a persisted cookie jar (e.g. `@aws-amplify`-style
  cookie policy or manual cookie storage), or OKHttp cookiejar on Android.
  No backend change is needed — the API already answers token refresh at
  `token/refresh/` and keeps the JWT in cookies.
- Alternatively, expose tokens in the login **response body** (`access_token`
  payload) and use `Authorization: Bearer` on native — the backend accepts
  both; the only new work is mobile-side header plumbing.

**Decision needed before mobile begins:** cookie-jar vs Bearer headers. Do
**not** build mobile around a third scheme; do not rebuild auth.

## 2. CSRF on mobile

The double-submit guard (`NaijaBay.middleware.CsrfGuardMiddleware`) applies
**only when auth cookies ride along**. A mobile client that stores tokens in
`Authorization` (no cookie jar) is out of CSRF scope entirely — no code
change required. If mobile carries the cookies, it must mirror the cookie jar
into an `X-CSRFToken` header like the web interceptor does.

## 3. Google Sign-In recommendation (not implemented)

Google Sign-In belongs at the **identity layer**, not the API surface:

1. Mobile completes a native OAuth2 flow with Google (gets an `id_token`).
2. The backend **verifies** the token against Google's JWKS (`google-auth-library-python`).
3. On success, the backend links/creates the NaijaBay user and issues the
   **same cookie JWT pair** (or response-body tokens) as email login — one
   auth architecture, no second system.
4. email stays the login identifier (`ACCOUNT_LOGIN_METHODS = {"email"}`).

Google's identity UX cannot be safely replicated by posting an email string.
The server-side verification step is non-negotiable (anyone can forge a
client-sent email otherwise).

## 4. API inventory for mobile

All base paths are under `/api/v1/`. Pagination is `PageNumberPagination`
(page size 20; messaging caps at 100).

| Area | Endpoints (methods) |
| --- | --- |
| Auth | `accounts/auth/login/` (POST), `registration/`, `logout/`, `token/verify/`, `token/refresh/`, `user/` (GET/PATCH/PUT), `password/change/`, `password/reset/`, `password/reset/confirm/`, `registration/verify-email/`, `registration/resend-email/`, `user/<pk>/` (public profile) |
| Products | `products/` (GET list), `products/featured/`, `products/deals/flash/`, `products/categories/`, `products/create/` (POST), `products/detail/<slug>/` (GET/PATCH/DELETE), `products/create/images/` (upload), `products/update/images/<id>/`, `products/image/delete/<id>/`, `products/my-listings/`, `products/favorites/`, `products/recently-viewed/`, `products/rate/<slug>/`, `products/report/<slug>/` |
| Taxonomy | `core/attributes/` (sell-form specs) |
| Stores/social | `accounts/auth/create-store/`, `my-store/`, `store-detail/<slug>/`, `followers/<pk>/`, `following/<pk>/`, `core/toggle-favorite-product/<slug>/`, `core/toggle-follow-user/<id>/` |
| Cart & orders | `orders/cart/` (GET/DELETE), `orders/cart/items/` (POST), `orders/cart/items/<id>/` (PATCH/DELETE), `orders/checkout/` (POST), `orders/` (list), `orders/<ref>/`, `orders/<ref>/cancel/` (POST), `orders/sales/`, `orders/sales/<id>/status/` |
| Payments | `payments/orders/<ref>/initialize/` (POST), `payments/boost/plans/`, `payments/boost/initialize/` (POST), `payments/boost/my/`, `payments/verify/<ref>/`, `payments/webhook/` (Paystack only) |
| Messaging | `messaging/` (list/create conversations), `messaging/unread-count/`, `messaging/<id>/`, `messaging/<id>/messages/` (GET/POST incl. image & voice attachments), `messaging/<id>/read/` |
| Notifications | `accounts/auth/notifications/`, `core/mark-*-notification-*/`, `core/delete-*-notification*/` |

### Readiness gaps / decisions before mobile
- **No pagination cursors** — mobile infinite scroll should unwrap
  `next/previous` (page-based pagination exists and works).
- **Product mutations are JSON + multipart only** (no video, no draft server-side).
- **Optimistic chat** — WebSocket channel exists at `ws/chat/<id>/`; mobile
  needs its own socket client.
- **File uploads** reuse `media/upload-initiate/` (direct-to-storage with the
  `keys` attach flow already used by web).
- **Category browsing**: `products/categories/` + `attributes/` are enough
  for the filter UX.

## 5. Direct-upload verification (Phase 5 answer)

Server-side we currently **validate structure + existence**, not bytes, for
direct uploads (multipart uploads get full Pillow sniffing). The risk is a
file that is a valid MIME polyglot stored but displayed/served as an image —
low severity since display is via `<img>`/audio tags (no execution surface).
If ever needed: Cloudinary upload callbacks (`eager` delivery check) or a
16-byte range sniff via `storage.open(key,'rb')` — do not download whole
files for every attach. Not a launch blocker.

## 6. What mobile must NOT redo
Do not rebuild: auth (cookies + refresh in use), CSRF semantics (token
double-submit is browser-only), payments (Paystack verify is server-side),
object permissions, or the attribute system. Read
[Backend/ENDPOINTS.md](Backend/ENDPOINTS.md), [UNDERSTAND.md](UNDERSTAND.md)
and [SCALLING.md](SCALLING.md) before writing a line of mobile code.

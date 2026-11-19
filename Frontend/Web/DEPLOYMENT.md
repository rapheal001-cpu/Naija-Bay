# NaijaBay Web — Deployment Guide

## Build

Node.js 20+, then:

```powershell
npm install
npm run lint
npm run build
```

The production build is written to `dist/` (do not commit it). Build with the
production API base:

```env
VITE_BASE_URL=https://api.naijabay.com
```

Vite inlines `VITE_*` values at build time — rebuild after changing them and
never put secrets in frontend env files.

## Host requirements

- Serve `dist/` as a static site.
- **SPA fallback:** every client-side route (`/products`, `/sell`, `/profile`,
  `/product/detail/:slug`, `/safety`, …) must serve `index.html`. For Netlify /
  Cloudflare Pages add `public/_redirects` with `/*  /index.html  200`; for other
  hosts add the equivalent rewrite rule.
- **Cache headers:** `index.html` must be `no-cache`; fingerprinted `/assets/*`
  can be cached immutably. Otherwise a stale HTML file can reference chunks the
  new build removed.
- Serve everything over HTTPS.

## Backend cross-origin settings

The API host must appear in Django's `ALLOWED_HOSTS`; the web origin must appear
exactly (scheme + host, no path) in both `CORS_ALLOWED_ORIGINS` and
`CSRF_TRUSTED_ORIGINS`. In production the auth cookies are `Secure`, `HttpOnly`
and `SameSite=None`, so prefer a same-site pair such as `app.naijabay.com` and
`api.naijabay.com`. Cross-site cookies can be blocked by browser privacy settings.

## Auth and cookies

Login, logout and token refresh hit the API origin directly so cookies are set
on the API domain. Axios uses `withCredentials: true` and mirrors the CSRF
cookie into `X-CSRFToken` for unsafe methods. Keep the web and API hostnames
identical in development (`localhost`) for the same reason.

## Media

The API returns storage URLs directly; do not add a `/media/` rewrite on the
static host. Large uploads use the direct-to-storage flow:

1. `POST /api/v1/storage/media/uploads/initiate/` (backend signs the request).
2. Browser uploads straight to Cloudinary or S3 (multipart parts where needed).
3. Domain create/update endpoints receive the returned object key.

Django never proxies the file bytes. Keep bucket access private and credentials
backend-only; a signed URL is a bearer credential until it expires. See
[DEVELOPMENT.md](./DEVELOPMENT.md#media-and-uploads).

## Runtime notes

- Chat needs an ASGI backend (Daphne) and the WebSocket origin allow-list on the
  Django side. REST fallback keeps messaging usable when a socket drops.
- There is no service worker/offline bundle in this web client; network failures
  are surfaced through the `/network-error` route.
- Django admin is on the backend at `/admin/`; there is no separate staff SPA.
- `Backend/PRODUCTION.md` and root `SCALLING.md` cover the API deployment.

# Naija-Bay Backend — Production

> Paystack-backed, not Stripe. Everything here is specific to Naija-Bay's
> stack (Django + DRF + Daphne + Paystack). For the scaling runbook see
> [../SCALLING.md](../SCALLING.md); for the endpoint catalogue see
> [ENDPOINTS.md](ENDPOINTS.md).

## Environment variables (production)

| Variable | Required | Purpose |
| --- | --- | --- |
| `ENVIRONMENT` | yes | Must be `production` (enables secure cookies, strict hosts) |
| `DEBUG` | yes | Must be `False` |
| `SECRET_KEY` | yes | Django secret, strong random value |
| `ALLOWED_HOSTS` | yes | API domain(s), comma-separated |
| `CSRF_TRUSTED_ORIGINS` | yes | Web app origin(s) |
| `CORS_ALLOWED_ORIGINS` | yes | Web app origin(s) |
| `DATABASE_URL` | yes | PostgreSQL URL (SQLite is dev-only) |
| `REDIS_URL` | yes | Redis for Channels layer + cache |
| `MEDIA_STORAGE_BACKEND` | yes | `cloudinary` or `s3` (never AWS in dev) |
| `CLOUDINARY_CLOUD_NAME` / `API_KEY` / `API_SECRET` | when cloudinary | Cloudinary credentials |
| `AWS_*` bucket settings | when s3 | S3/R2 credentials + bucket CORS |
| `PAYSTACK_SECRET_KEY` | yes | Paystack secret key |
| `PAYSTACK_PUBLIC_KEY` | yes | Paystack public key (frontend) |
| `FRONTEND_URL` | yes | Web app URL for email links |

Invalid storage backends fail at startup — they never silently fall back.

## Paystack setup (one-time, platform owner)

1. Create the Paystack account and switch to **live mode** when ready
   (test and live keys are separate — do both).
2. Add one webhook endpoint:
   `https://<api-domain>/api/v1/payments/webhook/` for the
   `charge.success` event.
3. Copy the secret key into the host's environment as
   `PAYSTACK_SECRET_KEY` and redeploy.
4. Test with a real boost purchase; confirm the `WebhookEvent` row shows
   `succeeded` and the boost activates.

**What the webhook guarantees:**

- Signature-verified — unsigned deliveries are rejected.
- Every delivery writes a `WebhookEvent` (processing → succeeded/failed).
- The backend re-verifies with Paystack; the webhook body is never trusted.
- Payment is marked paid exactly once (conditional update + negative-amount
  check constraint).

## Deploy checklist

1. `migrate` on the fresh database.
2. `python manage.py seed_all` then `python manage.py attribute_definitions`
   (taxonomy + listings + 40 definitions / 133 options).
3. Serve with `daphne -p 8000 NaijaBay.asgi:application` (HTTP + WebSockets
   in one process).
4. Put Cloudflare in front (Full strict TLS, origin firewalled) — see
   [../SCALLING.md](../SCALLING.md).
5. Rebuild the frontend with the production `VITE_API_BASE_URL`.
6. Rehearse a database backup restore.

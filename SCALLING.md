# Scaling Naija-Bay to Millions of Users

> The complete production guide: Cloudflare, the app host, PostgreSQL,
> Redis, media storage, real-time chat, monitoring, and step-by-step
> configuration for every process.
>
> Companion to `UNDERSTAND.md` (what Naija-Bay is) — this file is *how to
> run it in production*.
>
> *"SCALLING" matches the exact file name used by the SkillStream project
> this guide is modeled on.*

---

## 1. Where Naija-Bay runs today

```
Users
  │
  ▼
[Edge: Cloudflare]  ── absorbs DDoS, rate-limits, terminates TLS
  │
  ▼
[App host]  https://<api-domain>
  ├─ Daphne (ASGI: HTTP API + WebSockets on one process)
  ├─ PostgreSQL (managed)
  ├─ Redis (managed — Channels layer + cache)
  └─ (optional) background worker for boost-expiry checks
         │
         ▼
   Cloudinary or S3/R2 (media storage, direct uploads)
         │
         ▼
     Paystack (payments + signed webhooks)
```

The frontend is a static Vite build, deployed separately (see §10).

---

## 2. Cloudflare setup (do this first)

Cloudflare sits **in front of the app host**. Do not expose the origin
directly:

1. Point the API hostname DNS at the host (proxied, orange cloud).
2. Set SSL mode to **Full (strict)** with a valid origin certificate.
3. Add a rate-limit rule on `/api/v1/auth/` and `/api/v1/payments/` —
   auth and payment endpoints are the abuse magnets.
4. Enable cache rules: cache `/api/v1/products/` GETs at the edge for
   30–60s only with a custom cache key on query string; never cache
   authenticated responses.

Origin firewall: allow Cloudflare IP ranges only.

---

## 3. Application hosting

One Daphne process serves both HTTP and WebSockets — that is the
production topology. `--workers 1` and scale by adding processes behind a
load balancer only when a single process saturates; Channels rooms are
group-based, so sticky sessions are not required, but Redis bound to the
channel layer must be shared by all workers.

```
daphne -p 8000 NaijaBay.asgi:application
```

Whitelisted hosts (`ALLOWED_HOSTS`) must include the public API domain;
`CSRF_TRUSTED_ORIGINS` must include the web app origin.

---

## 4. Database

- **Engine**: PostgreSQL in production (`DATABASE_URL`). SQLite is dev-only
  and concurrency-limited — never put SQLite behind multiple workers.
- **Migrations**: the schema is a single `0001_cutover_baseline` per app.
  Fresh environments: `migrate` then `seed_all` and
  `attribute_definitions`.
- **Connection pooling**: point `DATABASE_URL` at PgBouncer (transaction
  mode) when a connection pooler is available; keep
  `CONN_MAX_AGE=60`.
- **Indexes**: product browse paths are covered (`category_obj`,
  `subcategory_obj`, `state_obj`, `city_obj`, `user`, `purpose/status` on
  payments). Add a composite index on `(category_obj, subcategory_obj)`
  only when EXPLAIN shows a sequential scan under real data.

---

## 5. Redis: cache and Channels layer

One Redis instance serves both:

- **Channels layer** (`channels-redis`) — required for WebSocket fan-out
  across processes. In-memory layer is dev-only and single-process.
- **Django cache** (`django-redis`) — generation-based read cache from
  `NaijaBay/cache.py`. Generation bumps, not key deletion, invalidate.

Set both from the same `REDIS_URL`:

```
REDIS_URL=redis://default:password@<host>:6379/0
```

Verify: `redis-cli -u $REDIS_URL ping` → `PONG`.

---

## 6. Media storage

Development is **always** local. Production picks one backend:

```
MEDIA_STORAGE_BACKEND=cloudinary   # or: s3
```

- **Cloudinary**: needs `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`,
  `CLOUDINARY_API_SECRET`. The frontend uploads directly with signed
  fields — UI never blocks on the app server.
- **S3/R2**: needs bucket credentials and `AWS_*` settings; grant the
  bucket a CORS rule for direct browser uploads and presigned URLs.
- Never set an AWS backend in development. The allowlist in
  `NaijaBay/storage.py` rejects unknown values at startup.

---

## 7. Real-time chat

- WebSockets are served by the same Daphne process as the API; no extra
  service to run.
- With Redis as the channel layer, rooms span processes; presence and
  broadcast scale horizontally by adding Daphne workers.
- The REST API stays the source of truth — if a socket drops, the client
  falls back to REST and re-syncs on reconnect. No message loss model to
  maintain.
- Watch Channels metrics (connections, room sizes) before hitting
  connection-file-descriptor limits (raise `ulimit -n` with worker count).

---

## 8. Caching strategy

| Layer | What it caches | Invalidation |
| --- | --- | --- |
| Edge (Cloudflare) | Public product GETs, 30–60s | TTL |
| Django read cache | Querysets via `NaijaBay/cache.py` | Generation bump on write |
| Client (TanStack Query) | List pages, 5-min stale time | Query invalidation on mutation |

Never cache mutation responses. Facet counts are computed per request —
do not edge-cache them without preserving the filter query string.

---

## 9. Workers and scheduled jobs

Boost expiry is checked on read (`expire_boosts_if_due`) with a 60-second
cache guard, so no worker is required. If you add Celery later for
emails/thumbnails, it is a new service, not a bottleneck remover — add it
only when a user-facing flow needs background work.

---

## 10. Frontend deployment

The web app is a static Vite build:

```powershell
cd Frontend/Web
npm run build    # output: dist/
```

Deploy `dist/` to any static host. The build must be created with the
public API base:

```
VITE_API_BASE_URL=https://<api-domain>/api/v1
```

and that origin must appear in the backend's `CORS_ALLOWED_ORIGINS` and
`CSRF_TRUSTED_ORIGINS`.

---

## 11. Monitoring and errors

- **Backend**: structured logging to stdout; the `request_id` on API error
  responses (`{"code", "detail", "status", "request_id"}`) is the join key
  for log digs.
- **Health**: Django's `check` command for deploys; watch Daphne log error
  rate.
- **Paystack**: the `WebhookEvent` table is an audit trail per delivery
  (`processing`/`succeeded`/`failed`). Alert on `failed` rows older than
  5 minutes — Paystack retries deliveries, but a persistent failure means
  the secret/signature path is broken.
- **Backups**: daily PostgreSQL snapshots; test a restore before launch.

---

## 12. Launch checklist

- [ ] `ENVIRONMENT=production`, `DEBUG=False`, strong `SECRET_KEY`
- [ ] `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` set for both domains
- [ ] PostgreSQL + Redis provisioned; `DATABASE_URL`, `REDIS_URL` set
- [ ] `MEDIA_STORAGE_BACKEND` set (cloudinary or s3); CORS on the bucket
- [ ] `PAYSTACK_SECRET_KEY` set; webhook endpoint registered in Paystack
- [ ] `migrate` + `seed_all` + `attribute_definitions` run on the fresh DB
- [ ] Cloudflare in front, Full (strict) TLS, origin firewalled
- [ ] Frontend rebuilt with production `VITE_API_BASE_URL`
- [ ] Backup/restore rehearsed; error alerting wired

# Naija-Bay

A Nigerian online marketplace in the style of Jiji.ng (classifieds) and Temu (deals, discounts, ratings). Sellers list products, buyers browse, favorite, rate and chat with sellers.

| Part | Folder | Stack |
|---|---|---|
| API | `Backend/` | Django 6, Django REST Framework, auth_kit (cookie JWT), allauth, drf-spectacular |
| Web app | `Frontend/Web/` | React 19, Vite 8, Tailwind 4, Redux Toolkit, TanStack Query, Axios |
| Mobile app | `Frontend/Mobile/` | Not started (empty folder) |

```text
Naija-Bay/
├── UNDERSTAND.md           product, architecture, and handover explainer
├── SCALLING.md             production runbook
├── Backend/
│   ├── NaijaBay/         # settings, urls, ASGI, shared helpers, management/commands (seed commands)
│   ├── accounts/         # users, stores, follows, notifications
│   ├── products/         # products, images, ratings, reports, attribute filters
│   ├── messaging/        # buyer/seller conversations, messages, WebSocket chat
│   ├── orders/           # cart, orders, checkout
│   ├── payments/         # Paystack initialize/verify/webhook, boost plans
│   ├── core/             # states, cities, categories, attribute definitions
│   ├── images/           # screenshots of the web app (REA captures)
│   ├── run_server.py     # launcher only: Vite + Daphne (HTTP + WebSockets)
│   ├── run_migrations.py # development migration helper
│   ├── run_seed.py       # development seed helper
│   ├── manage.py
│   └── requirements.txt
└── Frontend/
    └── Web/
```

## Screenshots

Captured with REA from the live app (see [UNDERSTAND.md](UNDERSTAND.md#15-screenshots) for the full list):

| Desktop | Mobile |
| --- | --- |
| ![Home](Backend/images/home.png) | ![Home mobile](Backend/images/home-mobile.png) |
| ![Browse](Backend/images/browse.png) | ![Login](Backend/images/login.png) |
| ![Product page](Backend/images/product-page.png) | ![Register](Backend/images/register.png) |
| ![Sell](Backend/images/sell.png) | ![Messages](Backend/images/messages.png) |
| ![My Ads](Backend/images/my-ads.png) | |

**Want the product story, architecture, and handover checklist?**
Read [UNDERSTAND.md](UNDERSTAND.md) first. For production setup see
[SCALLING.md](SCALLING.md), [Backend/ENDPOINTS.md](Backend/ENDPOINTS.md),
and [Backend/PRODUCTION.md](Backend/PRODUCTION.md).

## Setup & Environment Guide

### Prerequisites
Windows or WSL/Linux with **Python 3.14**, **Node.js 20+**, and Git. Redis
is optional in development (the backend uses in-memory fallbacks).

### Backend installation

```powershell
cd Backend
py -m venv venv
.\venv\Scripts\Activate.ps1          # Windows; Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env                # first time only
```

### Frontend installation

```powershell
cd Frontend\Web
npm install
```

### The six environment files

**Backend** (`Backend/`): `.env` (local dev), `.env.production` (production —
loaded **only** when the OS environment has `ENVIRONMENT=production`),
`.env.example` (template, tracked). Values in any of these files never
override real process environment variables.

**Frontend** (`Frontend/Web/`): `.env` (local dev), `.env.production`
(production build), `.env.example` (tracked). Vite inlines Vite variables **at
build time** — rebuild after changing them. Frontend files contain **public
values only**; never put secrets there. A `.env.local` file is not used.

### Variable inventory

Backend (all read by `NaijaBay/settings.py` via python-decouple):

| Variable | Purpose |
| --- | --- |
| `ENVIRONMENT` | `development` / `production` — drives secure-cookie/HTTPS guard rails |
| `SECRET_KEY` | Signing secret for cookies/tokens. **Never reuse dev values in prod** |
| `DEBUG` | Must be `False` in production (fail-fast guard) |
| `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS` | Frontend/API domains |
| `DATABASE_URL` | PostgreSQL URL (empty = local SQLite) |
| `SITE_ID`, `TIME_ZONE`, `LANGUAGE_CODE` | Site/locale defaults |
| `JWT_ACCESS_TOKEN_LIFETIME` (min), `JWT_REFRESH_TOKEN_LIFETIME` (days) | Cookie session lengths |
| `MEDIA_STORAGE_BACKEND` | `local` (dev) \| `s3` \| `cloudinary` (production only) |
| `CLOUD_NAME`, `CLOUD_API_KEY`, `CLOUD_API_SECRET` | Cloudinary direct uploads |
| `AWS_*` (6 vars) | S3/R2-compatible storage (production only) |
| `EMAIL_*`, `DEFAULT_FROM_EMAIL` | SMTP (production; dev uses the console backend) |
| `PAYSTACK_SECRET_KEY` | Paystack (empty in dev = simulated test checkout) |
| `FRONTEND_URL` | Where Paystack sends buyers back after payment |
| `DELIVERY_FEE` | Flat delivery fee per order, in naira |
| `REDIS_URL` | Cache + Channels layer (empty = in-memory in dev) |

Frontend (public, build-time): `VITE_BASE_URL` (API origin) is the only
supported variable.

### Development vs production
Development: SQLite, `MEDIA_STORAGE_BACKEND=local`, console email, empty
`PAYSTACK_SECRET_KEY` (simulated checkout), `DEBUG=True`. Production:
PostgreSQL (`DATABASE_URL`), Redis, `DEBUG=False`, secure cookies + HTTPS
redirects, `PAYSTACK_SECRET_KEY=sk_live_…`, storage `cloudinary`/`s3`.

### Paystack test mode & local webhooks
Set a `sk_test_…` key in your `.env` to exercise the real checkout. Webhook
callbacks require a reachable HTTPS URL — record them from
`dashboard.paystack.com/#/settings/developers` at
`POST /api/v1/payments/webhook/` (signature verified HMAC-SHA512).

### Storage
`local` = `mediafiles/` on disk. `cloudinary`/`s3` = direct browser→provider
uploads with signed params; the backend stores only the key. Never enable AWS
backends in development.

### Database setup
`python manage.py migrate` — fresh DBs use the single `0001_cutover_baseline`
per app. Seed with `python manage.py seed_all` and
`python manage.py attribute_definitions`.

### Starting servers
Backend: `.\venv\Scripts\python.exe -m daphne -p 8000 NaijaBay.asgi:application`
(HTTP + WebSockets on one server). Frontend: `npm run dev` at
`http://localhost:5173`. Use the **same** hostname (`localhost`) for both —
cookies are scope-bound (see present-day notes on local auth).

### Tests
`python manage.py test payments` (32 tests, ~4 min, Paystack mocked),
`accounts`, `products`, `messaging`, `orders`, plus CSRF/axes suites.
Frontend: `npm run lint`, `npm run build`.

### Security notes
- Never commit `.env` / `.env.production` (root `gitignore` covers them).
- Rotate the dev `SECRET_KEY` if it was ever shared; rotate **all** payment/
  storage secrets on any suspected leak.
- Track the `django-axes` cool-off values in `settings.py`
  (`AXES_FAILURE_LIMIT`, `AXES_COOLOFF_TIME`) — see production guide.

### Production prerequisites
PostgreSQL, Redis, HTTPS (Cloudflare or host TLS), `MEDIA_STORAGE_BACKEND`,
SMTP, `PAYSTACK_SECRET_KEY=sk_live_…`, `ALLOWED_HOSTS`/origins set, backup
tested. Full checklist: [Backend/PRODUCTION.md](Backend/PRODUCTION.md).

### Troubleshooting
- `Not Found: /health` in server logs — harmless health-probe traffic.
- CSRF 403s in dev: open the app via `http://localhost:5173` (not `127.0.0.1`),
  and check `CORS/CSRF` origins match.
- Port already in use: `Get-NetTCPConnection -LocalPort 8000 | Stop-Process`.
- Lost seeded data: back up the current DB manually, then run `python manage.py migrate` and `python run_seed.py`.

## Quick start

### 1. Backend (Windows PowerShell)

```powershell
cd Backend
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

copy .env.example .env          # first time only

python run_migrations.py        # create + apply migrations
python run_seed.py              # seed development data (idempotent)
python run_server.py            # launcher: Vite + Daphne
```

`run_server.py` is a **launcher only** (same pattern as SkillStream): it starts
Daphne (HTTP API + WebSockets on port 8000) and the Vite dev server (port 5173),
and stops both when you press Ctrl+C. It does not check, migrate or seed — use
the two dedicated scripts above. To start a clean database, back up/remove
`Backend/db.sqlite3` yourself, then run the two scripts again.

`run_seed.py` runs the approved seed commands in dependency order (all under
`NaijaBay/management/commands/`):

1. `nigeria_states` — 36 states + FCT and their cities
2. `categories` — categories and sub-categories
3. `seed_boost_plans` — Paystack boost plans
4. `create_user` — admin and regular users with avatars and verified emails
5. `seed_products` — a store and at least 3 products per user
6. `seed_all` — sellers, buyers, follows, favourites, views, ratings, chats, reports, notifications
7. `attribute_definitions` — 40 definitions and 133 options

Every seed step is idempotent, so running it again does not create duplicates. Shared seed helpers live in private modules `_catalog.py` and `_images.py` next to the commands.

### 2. Frontend

```powershell
cd Frontend\Web
npm install
npm run dev
```

The frontend reads the API address from `Frontend/Web/.env`:

```env
VITE_BASE_URL=http://localhost:8000
```

Open the app at **http://localhost:5173**. Use `localhost` for both the app and the API (not a mix of `localhost` and `127.0.0.1`), otherwise the browser treats them as different sites and the login cookies are not sent.

## Useful addresses

| What | URL |
|---|---|
| Web app | http://localhost:5173 |
| API root | http://localhost:8000/api/v1/ |
| Swagger docs | http://localhost:8000/api/v1/docs/ |
| ReDoc | http://localhost:8000/api/v1/redoc/ |
| Django admin | http://localhost:8000/admin/ |

## Demo logins

Local development only. Emails are already verified, so you can log in straight away.

| Account | Email | Password |
|---|---|---|
| Admin (superuser) | `admin@gmail.com` | `OnlyGod1@` |
| Sellers | `seedseller1@naijabay.test` ... `seedseller8@naijabay.test` | `TestPass123!` |
| Buyers | `seedbuyer1@naijabay.test` ... `seedbuyer8@naijabay.test` | `TestPass123!` |
| Generated users (about 50 in total) | printed as `first.lastNNN@gmail.com` in the database | `Password123@` |

## Development scripts

Run from the `Backend` folder.

| Script / option | What it does |
|---|---|
| `python run_migrations.py` | Check DB, generate migrations for local apps, apply them |
| `python run_migrations.py --check-only` | Report model changes without writing anything |
| `python run_seed.py` | Seed all development data (idempotent) |
| `python run_seed.py --images` | Also generate placeholder product photos (6-10 each, slower) |
| `python run_seed.py --clear` | Clear seeded data first, then reseed |
| `python run_server.py` | Launch Vite + Daphne (HTTP + WebSockets) |
| `--host`, `--port` | Daphne interface/port (default `127.0.0.1:8000`) |
| `--no-frontend` | Do not start Vite (run `npm run dev` yourself) |
| `--preflight-only` | Check prerequisites and print the plan without starting anything |

Cleaning artifacts: from the project root run `python clean_project.py` (dry run)
or `python clean_project.py --delete` (removes caches, generated migrations,
SQLite DB/backups, `logs/`, `staticfiles/`, `mediafiles/` and `Frontend/Web/dist`).

## Seed commands

All live in `Backend/NaijaBay/management/commands/` (boost plans in `Backend/payments/management/commands/`) and can also be run alone with `python manage.py <name>`.

| Command | Seeds |
|---|---|
| `nigeria_states` | 36 states plus FCT, and their cities |
| `categories` | Categories and sub-categories |
| `create_user` | Admin and regular users, up to 50 in total (`--count`, `--password`; `--user --email --username --password` for one account) |
| `seed_products` | Products and stores for every user, at least 3 products each (`--username`, `--count`, `--images`, `--no-store`) |
| `seed_all` | Sellers, buyers, stores, follows, products, favorites, views, ratings, conversations, messages, reports and notifications (`--clear`, `--images`, `--users`, `--products-per-user`, `--conversations`, `--password`, `--seed`) |

## Configuration

Backend settings come from `Backend/.env` (copy `Backend/.env.example`). The important ones for local work are:

- `DEBUG=True`: without it, `ALLOWED_HOSTS` stays empty and every request is rejected.
- `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`: must include the frontend origin (`http://localhost:5173`).
- `DATABASE_URL`: leave empty for SQLite, set a URL for PostgreSQL.

Restart the server after changing `.env`. In development, emails (verification, password reset) are printed in the server console instead of being sent.

## Troubleshooting

- **"Bad Request (400)" on every page:** `Backend/.env` is missing or has `DEBUG=False`. Copy `.env.example` to `.env`.
- **"no such table" or "no such column":** the old `db.sqlite3` does not match the models. Back it up/remove it, then run `python run_migrations.py` and `python run_seed.py`.
- **Frontend requests go to port 5173 or fail with CORS errors:** check `Frontend/Web/.env` has `VITE_BASE_URL`, restart `npm run dev`, and make sure both sides use `localhost`.
- **Login works in Swagger but not in the app:** the browser is mixing `localhost` and `127.0.0.1`. Use one of them for both.
- **`pip install` complains about `requirements.txt`:** the file is saved as UTF-16. Re-save it as UTF-8.
- **Seeding is slow:** do not pass `--images` to `run_seed.py` (photos are optional).
- **`vite.config.js` proxy target:** it is correctly set to `http://localhost:8000`. It is not used while the app talks to the API through `VITE_BASE_URL`.

## More documentation

- `Backend/README.md`: API routes, throttling and environment details
- `Backend/QUICKSTART.md` and `Backend/DEVELOPMENT.md`: backend setup notes
- `Frontend/Web/README.md`: frontend structure and how to add an endpoint

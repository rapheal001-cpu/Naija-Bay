# Understanding Naija-Bay

> **A professional Nigerian classifieds marketplace in the style of Jiji.ng.**
> Naija-Bay gives buyers a place to browse, search, and compare listings from
> sellers across Nigeria, gives sellers a place to post free ads, chat with
> buyers, and promote listings with paid boosts, and gives the platform owner
> one Paystack-powered way to monetize ad boosts and orders.

This document is written for two audiences at once:

- **A buyer or client** who wants to know what the product does and what they
  would own.
- **A developer or operator** who needs to understand how the backend is wired
  and what still needs attention before launch.

Everything below reflects the code in this repository. Features that are not
implemented are listed honestly under [Known gaps](#14-known-gaps-and-honest-limitations),
not presented as if they exist.

---

## Table of contents

1. [The one-paragraph pitch](#1-the-one-paragraph-pitch)
2. [The problem Naija-Bay solves](#2-the-problem-naija-bay-solves)
3. [Who it is for](#3-who-it-is-for)
4. [What the product does](#4-what-the-product-does)
5. [System architecture](#5-system-architecture)
6. [Backend apps](#6-backend-apps)
7. [The database](#7-the-database)
8. [Authentication and permissions](#8-authentication-and-permissions)
9. [Payments: Paystack boosts](#9-payments-paystack-boosts)
10. [Real-time chat](#10-real-time-chat)
11. [Media uploads and storage](#11-media-uploads-and-storage)
12. [Caching and the N+1 rule](#12-caching-and-the-n1-rule)
13. [Seeding](#13-seeding)
14. [Known gaps and honest limitations](#14-known-gaps-and-honest-limitations)
15. [Documentation map](#15-documentation-map)

---

## 1. The one-paragraph pitch

Naija-Bay is a Nigerian classifieds marketplace: anyone can browse thousands
of ads — phones, cars, fashion, electronics, real estate, jobs, and services —
filtered by category, state, city, and structured attributes. Registered
sellers post free ads, chat directly with interested buyers, and optionally
pay for ad boosts through Paystack so their listings surface first. Buyers can
favourite listings, rate products, report abuse, save items to a cart, and
check out through Paystack. Everything runs on a Django REST backend with
real-time WebSocket chat and a React web app.

## 2. The problem Naija-Bay solves

Nigeria's informal trade happens in WhatsApp broadcasts, Instagram DMs, and
anonymous Facebook groups — places where buyers cannot compare prices,
filters, or seller reputation, and where scams are hard to report. Jiji.ng
proved the model but charges for visibility. Naija-Bay keeps posting free,
adds structured attribute filters (so "2-bedroom flats in Lekki" actually
narrows results), seller ratings, abuse reporting, and a chat layer that stays
on-platform — so if something goes wrong, the platform can see the thread.

## 3. Who it is for

- **Buyers** — anyone shopping for new or used goods across 36 states + FCT.
- **Sellers** — individuals and small shops listing products, vehicles,
  properties, or services; verifying their store builds trust.
- **The platform owner** — operates the marketplace, reviews abuse reports,
  manages boost plans, and collects revenue via Paystack.

## 4. What the product does

- **Browse and search** — public listings with category, subcategory, state,
  city, price, condition, and attribute filters; full-text search; facet
  counts so filters show live result sizes; infinite scrolling on the browse
  page.
- **Post and manage ads** — sellers create listings with up to 10 photos,
  negotiable pricing, original-price discounts, contact methods, and optional
  structured specifications (e.g. RAM/storage for phones). Owners edit or
  delete their ads from *My Ads*.
- **Chat with sellers** — every listing has a *Message Seller* action that
  opens a 1:1 conversation. Messages support multi-image sends (up to 10),
  browser-recorded voice notes, read receipts, and live delivery over
  WebSockets with a REST fallback.
- **Favourites, ratings, reports** — buyers save listings, rate products
  1–5 stars, and report scam/wrong-category/duplicate listings; sellers get
  notifications and can see their reputation.
- **Cart, orders, checkout** — buyers save items to a cart, place orders, and
  pay through Paystack. Boost purchases are a separate, simpler flow.
- **Ad boosts** — sellers pay (Paystack) to promote a listing for a fixed
  period; boosted listings surface first. Boost expiry is checked
  automatically.
- **Stores and follows** — sellers get a store page; buyers follow sellers
  and get notified of new listings.
- **Verified attribution** — every listing carries relational
  `category_obj`, `subcategory_obj`, `state_obj`, and `city_obj` foreign keys
  with legacy string columns derived from them, so filters never disagree
  with the rendered taxonomy.

## 5. System architecture

```
Browser (React + Vite, :5173 in dev)
   │  REST /api/v1/   +   WebSocket /ws/chat/<id>/
   ▼
Daphne (ASGI: HTTP API + WebSockets, :8000)
   ├─ Django REST Framework   (auth, CRUD, filters, serializers)
   ├─ Channels                (chat rooms, presence)
   ├─ PostgreSQL              (production, via DATABASE_URL)
   ├─ Redis                   (prod: cache + Channels layer; dev: in-memory)
   └─ Media storage           (dev: local; prod: Cloudinary or S3/R2)
          │
          ▼
       Paystack (boost + order payments, signed webhooks)
```

In development everything is local: SQLite, in-memory channel layer, and local
media storage. Production switches each backend via environment variables —
see [SCALLING.md](SCALLING.md).

## 6. Backend apps

| App | Responsibility |
| --- | --- |
| `accounts` | Users, email verification, stores, follows, notifications, password flows |
| `products` | Listings, images, favourites, views, ratings, reports, attribute filters/facets |
| `core` | Category, SubCategory, State, City, AttributeDefinition/Option, ProductAttribute |
| `messaging` | Conversations, messages, WebSocket consumer, attachment support |
| `orders` | Cart, cart items, orders, order items, checkout |
| `payments` | Paystack initialize/verify/webhook, boost plans, listing boosts |
| `NaijaBay` | Settings, root URLs, ASGI, storage/cache/middleware, seed commands |

Per-app documentation lives in each app's folder; the API surface is catalogued
in [Backend/ENDPOINTS.md](Backend/ENDPOINTS.md).

## 7. The database

- **SQLite** in development (`db.sqlite3`), **PostgreSQL** in production via
  `DATABASE_URL`.
- Every app carries a single `0001_cutover_baseline` migration — the whole
  schema generates from the current models in one step. After the cutover
  reset, seed data is recreated with `seed_all` (see §13).
- The `Product` table is the heart of the cutover: legacy string columns
  (`category`, `sub_category`, `state`, `city`) are **derived from** the
  relational FKs (`category_obj`, `subcategory_obj`, `state_obj`, `city_obj`)
  in the serializer, never the other way. The API contract keeps the
  underscore string format, so the frontend never changed.
- `Payment` carries a `payment_amount_non_negative` check constraint, and
  `WebhookEvent` records processing state (`processing`/`succeeded`/`failed`)
  for every Paystack delivery.

## 8. Authentication and permissions

- **Cookie JWT** via `auth_kit` + SimpleJWT: `access_token` and
  `refresh_token` HttpOnly cookies; the WebSocket layer authenticates from
  the same cookie.
- Registration requires email verification; seeded test accounts are
  pre-verified.
- Anonymous visitors browse public listings. Actions (favourite, chat,
  cart, checkout) require sign-in; only listing owners can edit or delete
  their ads.
- The frontend guards account routes, re-verifies the session on load, and
  turns account-only actions for anonymous users into sign-in prompts. The
  backend is always the final authority.

## 9. Payments: Paystack boosts

Naija-Bay uses **Paystack** (not Stripe — SkillStream's provider does not
apply here). Two purchase kinds exist:

1. **Ad boosts** — a seller picks a `BoostPlan`, the backend creates a
   `Payment` priced from the plan (never from the client), initializes a
   Paystack transaction, and activates the boost on verification.
2. **Orders** — checkout creates a `Payment` for the order total; the
   signed `charge.success` webhook is the single source of truth that marks
   payment and order paid.

Webhook handling is idempotent: every delivery writes a `WebhookEvent` row,
re-verifies with Paystack (the webhook body is never trusted), and marks the
payment paid exactly once via a conditional update. Amount, currency, and
reference are all re-checked server-side.

To go live you need `PAYSTACK_SECRET_KEY` and the webhook endpoint
registered in the Paystack dashboard — see [Backend/PRODUCTION.md](Backend/PRODUCTION.md).

## 10. Real-time chat

- **Transport**: WebSocket-first (`/ws/chat/<conversation_id>/`) with a
  REST fallback when the socket is unavailable; the REST API stays the
  source of truth.
- **Auth**: cookie JWT via `JWTAuthMiddlewareStack`; close codes are
  documented in `messaging/consumers.py` (4401 unauthenticated, 4404 missing,
  4403 non-participant).
- **Attachments**: `Message.attachment_type` (`image`/`audio`),
  `attachment_url`, and `duration_ms`. The browser records voice notes with
  `MediaRecorder`; images upload through the direct-to-storage pipe.
- **Lifecycle**: sending a message marks the thread read for the sender and
  notifies the recipient.

## 11. Media uploads and storage

- **Development**: local `MEDIA_ROOT` storage — uploads never hit AWS.
- **Production**: `MEDIA_STORAGE_BACKEND` selects `cloudinary` or `s3`
  (S3/R2-compatible). The switch is an allowlist; an invalid value fails at
  startup instead of silently falling back.
- **Direct uploads**: the frontend asks the backend to initiate an upload,
  streams the file straight to storage, and only then attaches the URL — so
  image uploads never block on the app server. Progress is streamed back to
  the Sell form and the chat composer, with a server-upload fallback when
  the direct path is unreachable.

## 12. Caching and the N+1 rule

- Every hot queryset is built with `NaijaBay/queryset_helper.py` —
  `select_related`/`prefetch_related` are baked in, never bolted on after
  the fact. Query-count regression tests lock the budget in.
- Read-through caching uses `NaijaBay/cache.py` with generation-based
  invalidation (Redis in production, in-memory in dev).
- Facet counts are computed per request from the filtered queryset; they
  stay correct because the N+1 budget keeps the underlying query flat.

## 13. Seeding

All seed commands live under **`Backend/NaijaBay/management/commands/`**
(the project package — same pattern as SkillStream's `skillstream/`
package). One command rebuilds the whole marketplace:

```powershell
cd Backend
.\venv\Scripts\python.exe manage.py seed_all --users 8 --products-per-user 12
.\venv\Scripts\python.exe manage.py attribute_definitions
```

Test accounts (idempotent, password `TestPass123!`):
`seedbuyer1@naijabay.test` and `seedseller1@naijabay.test` (also
`seedseller8@naijabay.test`). The other commands — `categories`,
`nigeria_states`, `seed_products`, `create_user`, `backfill_product_fks` —
are the individual pieces `seed_all` composes.

## 14. Known gaps and honest limitations

- **No refunds ledger** — boosts are final-sale by design; refunds, if ever
  needed, require a migration and a product decision first.
- **Facet counts are per-request** — correct but not cached; a Redis layer
  for facets is a future optimization, not a bug.
- **Threads longer than 100 messages** cap at the messages `page_size`
  (100); older history needs an older-messages fetch UI.
- **Mobile app** — `Frontend/Mobile/` is an empty folder; only the web app
  ships.
- **Legacy strings persist** — the API still returns underscore strings
  for compatibility; dropping those columns is a separate, explicitly
  approved contract change.

## 15. Screenshots

Captured with REA from the live app (desktop 1440px, fed with seeded data):

| Screenshot | Page |
| --- | --- |
| [home.png](Backend/images/home.png) | Home — search hero, categories, featured ads |
| [browse.png](Backend/images/browse.png) | Browse — filters, sort, product grid |
| [product-page.png](Backend/images/product-page.png) | Listing detail — gallery, price, seller card |
| [sell.png](Backend/images/sell.png) | Post a free ad — photos, basic info, pricing |
| [messages.png](Backend/images/messages.png) | Chat inbox — conversation list and thread |
| [my-ads.png](Backend/images/my-ads.png) | My Ads — stats, status tabs, edit/delete |
| [login.png](Backend/images/login.png) | Sign in — split-screen brand panel |
| [register.png](Backend/images/register.png) | Create account |
| [home-mobile.png](Backend/images/home-mobile.png) | Home on mobile — bottom navigation |

## 16. Documentation map

| Doc | What it covers |
| --- | --- |
| [README.md](README.md) | Quick start and repo tour |
| [UNDERSTAND.md](UNDERSTAND.md) | This file — product, architecture, handover |
| [SCALLING.md](SCALLING.md) | Production runbook (Cloudflare, host, DB, cache, realtime, workers, monitoring) |
| [Backend/ENDPOINTS.md](Backend/ENDPOINTS.md) | Full API reference |
| [Backend/PRODUCTION.md](Backend/PRODUCTION.md) | Production environment and Paystack setup |
| [Backend/DEVELOPMENT.md](Backend/DEVELOPMENT.md) | Local development guide |
| [Frontend/Web/README.md](Frontend/Web/README.md) | Web app overview |

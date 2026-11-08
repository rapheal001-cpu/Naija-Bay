# Naija-Bay API — Endpoint Reference

Base: `/api/v1/`, trailing slash enforced. Auth: JWT in `access_token` /
`refresh_token` HttpOnly cookies (auth_kit). Unless marked public, the DRF
default is `IsAuthenticated`.

Docs UI: `/api/v1/docs/` · schema: `/api/v1/schema/` · ReDoc: `/api/v1/redoc/`.
The browsable API and auth UI exist only when `DEBUG=True`.

## Conventions

- List endpoints are paginated with DRF `PageNumberPagination`:
  `?page=<n>` → `{count, next, previous, results}`. Page size is fixed at
  **20** (the browse page uses this page size with the infinite-scroll
  client; the `next` cursor drives the sentinel).
- Only messaging message lists accept `?page_size=` (default 50, max 100);
  threads longer than 100 messages still cap at 100.
- Permission columns below: **public** = anonymous read allowed,
  **user** = any signed-in account, **owner** = listing owner,
  **participant** = conversation participant.
- Error responses under `/api/...` always stay JSON:
  `{"code", "detail", "status", "request_id"}`. Browser navigations outside
  `/api/` receive branded HTML error pages; send `Accept: application/json`
  or `X-Requested-With: XMLHttpRequest` to force JSON elsewhere.

## Quick reference

### Accounts & auth (`/api/v1/accounts/auth/`)

| Method | Path | Permission | Purpose |
|---|---|---|---|
| POST | `/register/` | public | Create account (email verified required) |
| POST | `/login/` | public | Cookie JWT login |
| POST | `/logout/` | user | Blacklist refresh token |
| POST | `/verify-email/<key>/` | public | Verify email address |
| POST | `/password/change/` | user | Change password |
| POST | `/password/reset/` | public | Request reset email |
| POST | `/password/reset/confirm/` | public | Confirm reset with token |
| GET/PATCH | `/profile/` | user | Read/update own profile |
| GET | `/profile/<username>/` | public | Read public profile |
| GET | `/stores/` | public | List stores |
| GET/POST | `/follows/` | user | Follow/unfollow sellers |
| GET | `/notifications/` | user | List notifications |
| GET | `/unread/` | user | Unread counts (messages + notifications) |

Test accounts after seeding: `seedseller1@naijabay.test`,
`seedbuyer1@naijabay.test` — password `TestPass123!`.

### Products (`/api/v1/products/`)

| Method | Path | Permission | Purpose |
|---|---|---|---|
| GET | `/` | public | Browse listings (filters below) |
| GET | `/featured/` | public | Featured/promoted listings |
| GET | `/<slug>/` | public | Listing detail |
| POST | `/` | user | Create listing |
| PATCH | `/<slug>/` | owner | Edit listing |
| DELETE | `/<slug>/` | owner | Delete listing |
| GET | `/my-listings/` | user | My ads |
| GET | `/favorites/` | user | Favourited listings |
| GET | `/recent/` | user | Recently viewed |
| POST | `/<slug>/favorite/` | user | Toggle favourite |
| POST | `/<slug>/report/` | user | Report abuse |
| POST | `/<slug>/boost/` | owner | Start a Paystack boost |
| POST | `/<slug>/views/` | user | Record a view |

**Browse filters.** Standard: `category`, `sub_category`, `state`, `city`,
`condition`, `min_price`, `max_price`, `search`, `ordering`. Structured
attributes (added by the cutover): `attr_<slug>` (exact match),
`attr_<slug>_min` / `attr_<slug>_max` (ranges), `attr_<slug>__in`
(multi-value). `?facets=1` adds live `facets` counts with per-definition
exclusion and multiselect `__in` counting. Bad numeric attributes return
400.

**Create/update.** `category`, `sub_category`, `state`, `city` accept the
legacy underscore strings; the serializer resolves them to the relational
FKs and derives the stored strings back — the FK is the source of truth,
the string never disagrees. `attributes` is optional for legacy
compatibility; when supplied, unknown slugs or out-of-range values are
rejected with 400.

### Core taxonomy & attributes (`/api/v1/core/`)

| Method | Path | Permission | Purpose |
|---|---|---|---|
| GET | `/categories/` | public | List categories |
| GET | `/categories/<slug>/` | public | Category detail |
| GET | `/attributes/` | public | Attribute definitions for `?category=&sub_category=` |

### Messaging (`/api/v1/messaging/`)

| Method | Path | Permission | Purpose |
|---|---|---|---|
| GET | `/conversations/` | user | List conversations (unread counts, last-message preview; image attachments show a thumbnail + `Photo` label, voice notes show `Voice note`) |
| POST | `/conversations/` | user | Start/open a conversation |
| GET | `/conversations/<id>/messages/` | participant | List messages (page size 100) |
| POST | `/conversations/<id>/messages/` | participant | Send text **or** attachment message |

**Send body.** Either text (`body`, 1–4000 chars) or an attachment message:
`attachment_type` (`image`|`audio`), `attachment_url` (required with a
type), `duration_ms` (voice notes). Empty text with no attachment is
rejected (400). WebSocket: `ws://<host>/ws/chat/<conversation_id>/` with
the same payload shape; cookie-JWT auth. Close codes: 4401
unauthenticated, 4404 missing conversation, 4403 non-participant.

### Orders (`/api/v1/orders/`)

| Method | Path | Permission | Purpose |
|---|---|---|---|
| GET | `/cart/` | user | Read cart |
| POST | `/cart/items/` | user | Add item |
| DELETE | `/cart/items/<id>/` | user | Remove item |
| POST | `/checkout/` | user | Place order + start Paystack payment |
| GET | `/orders/` | user | Order history |
| GET | `/orders/<id>/` | user | Order detail |

### Payments (`/api/v1/payments/`)

| Method | Path | Permission | Purpose |
|---|---|---|---|
| GET | `/boost-plans/` | public | List boost plans |
| POST | `/boost/` | owner | Start a boost (Paystack initialized server-side) |
| GET | `/verify/<reference>/` | user | Verify a payment (re-checks Paystack) |
| POST | `/webhook/` | public (signed) | Paystack signed webhook — idempotent via `WebhookEvent` |
| GET | `/history/` | user | Payment history |

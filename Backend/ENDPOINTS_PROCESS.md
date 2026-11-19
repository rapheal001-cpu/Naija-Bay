# NaijaBay — Endpoints Process Reference

Per-endpoint reference: what goes in and what comes out. Companion to
[ENDPOINTS.md](ENDPOINTS.md), which lists every route.

**Base:** `/api/v1/` (trailing slash enforced)
**Auth:** JWT cookies named `access` and `refresh` (HttpOnly). Login does not
return tokens in the JSON body.
**Default permission:** `IsAuthenticated`; public reads opt in explicitly.
**Pagination:** `?page=<n>` → `{count, next, previous, results}`, page size 20.
Only message lists accept `?page_size=` (default 50, max 100).
**Errors:** `{"code", "detail", "status", "request_id"}`.

---

## 1. Authentication (`/api/v1/accounts/auth/`)

### POST `/registration/`
**Auth:** No · **Body:** `{email, username, password1, password2}`
**Out:** `201` with a detail message; verification email is sent (console backend in development).

### POST `/verify-email/<key>/`
**Auth:** No · **Out:** `200` `{"detail": "Success! Your email is verified."}`

### POST `/resend-email/`
**Auth:** No · **Body:** `{email}` · **Out:** `200` detail.

### POST `/login/`
**Auth:** No · **Body:** `{email, password}` · **Out:** `200`, sets `access`/`refresh` cookies; user object in body. Throttled (`login`: 100/day) and protected by django-axes (5 failures → 30-minute cool-off).

### POST `/logout/`
**Auth:** Yes · **Out:** `200`; blacklists the refresh token and clears cookies. Requires CSRF token/Origin.

### GET/PATCH `/user/`
**Auth:** Yes · **Out:** profile object. PATCH accepts avatar, names, phone, address, state.

### GET `/user/<id>/`
**Auth:** Yes · **Out:** public profile of another user.

### Password flows
`POST /password/change/` (`old_password`, `new_password1`, `new_password2`),
`POST /password/reset/` (`email`), `POST /password/reset/confirm/`
(`uid`, `token`, `new_password1`, `new_password2`).

---

## 2. Products (`/api/v1/products/`)

### GET `/`
**Auth:** Public · **Query:** `search`, `category`, `sub_category`, `state`, `city`,
`condition`, `min_price`, `max_price`, `sort`, `delivery_available`,
`verified_seller`, `negotiable`, `discounted`, `page`, `facets=1`, `attr_<slug>`
(and `_min`, `_max`, `__in`).
**Out:** `200` paginated products. Each product includes `images`,
`average_rating`, `total_ratings`, `views_count`, `is_favorited`, `attributes`,
plus presentation fields `badge`, `posted_ago`, `location_label`,
`is_draft`, `moderation_status`. `?facets=1` adds live `facets` counts.

### GET `/detail/<slug>/`
**Auth:** Public · **Out:** full product including seller (`product_user`), all
images, attributes, and the fields above.

### POST `/create/`
**Auth:** Yes · **Body:** product fields; `is_draft` accepted; category/state/city
accept legacy strings resolved to relational FKs. **Out:** `201`.

### POST `/create/images/`
**Auth:** Yes · **Body:** multipart `images[]` files and/or `keys[]` direct-upload
object keys. **Out:** `201`. Keys must be `product-image` keys owned by the caller.

### POST `/rate/<slug>/`, `/report/<slug>/`, `/<slug>/favorites/`
**Auth:** Yes · **Out:** `200/201`; rating is 1–5, report accepts `reason` and `details`.

### GET `/my-listings/`, `/favorites/`, `/recently-viewed/`
**Auth:** Yes · **Query:** `status`, `page` · **Out:** paginated lists.

---

## 3. Core, feedback and verification

### GET `/api/v1/core/attributes/`
**Auth:** Public · **Query:** `category`, `sub_category` · **Out:** definitions with options.

### POST `/api/v1/core/toggle-favorite-product/<slug>/`, `/toggle-follow-user/<id>/`
**Auth:** Yes · **Out:** `200` with the new state.

### Feedback (`/api/v1/accounts/auth/`)
- `GET /feedback/?seller=<id>` — public, approved reviews only.
- `POST /feedback/create/` — `{seller, rating, comment}` → `201` (status `pending`).
- `PATCH|DELETE /feedback/<id>/` — author only; editing resets to `pending`.
- `POST /feedback/<id>/appeal/`, `/respond/` — seller only.

### Saved searches (`/api/v1/accounts/auth/`)
`GET/POST /saved-searches/` — `{name, query_params, notify}`; `PATCH|DELETE /saved-searches/<id>/`.

### Verified ID (`/api/v1/accounts/auth/`)
`POST /verification/submit/` — multipart `id_type`, `id_number`, plus `selfie`/`selfie_key` and `document`/`document_key` → `201` (pending).
`GET /verification/me/` — current status + `verified` flag.

---

## 4. Messaging (`/api/v1/messaging/`)

### GET/POST `/`
**Auth:** Yes · **POST body:** `{product, message}` → opens/reuses a conversation.
**GET out:** conversations with last-message preview and unread counts.

### GET/POST `/<id>/messages/`
**Auth:** conversation participant · **POST body:** `{body}` or
`{attachment_type: image|audio, attachment_url, duration_ms}` → `201`.
Chat object keys must be owned `chat-image`/`chat-audio` keys.

### POST `/<id>/read/` and `/<id>/clear/`
**Auth:** participant · **Out:** `200`. `read` marks incoming messages read and
emits `messages_read` to the other party. `clear` hides the thread only for the
caller (`ConversationUserState.deleted_at`); a new message restores it.

### GET/POST `/blocks/` and DELETE `/blocks/<id>/`
**Auth:** Yes · **POST body:** `{"user": <id>}` → `201`
`{id, blocker, blocked_user, created_at}`. Blocking hides the conversation for
both users, closes live sockets with 4403, prevents new conversations and new
messages. DELETE → `204`.

### WebSocket `/ws/chat/<conversation_id>/` and `/ws/chat/`
Cookie JWT auth. Client: `message`, `typing` (`is_typing`), `read`. Server:
`message`, `typing`, `messages_read`, `conversation_blocked`, `error`; inbox:
`message`, `unread`, `messages_read`, `conversation_cleared`,
`conversation_blocked`. Close codes: 4401 unauthenticated, 4404 missing
conversation, 4403 access revoked mid-session, 1013 channel layer unavailable.
Membership **and block state are re-checked on every event**. Per-socket rate
limits: messages 20/10s, typing 40/10s, read 30/10s. REST remains the source of
truth; the frontend falls back to it when a socket is unavailable.

---

## 5. Orders, Safe Deal and payments

### Cart / checkout (`/api/v1/orders/`)
`GET /cart/` · `POST /cart/items/` `{product_id, quantity}` · `PATCH|DELETE /cart/items/<product_id>/`
· `DELETE /cart/` · `POST /checkout/` `{recipient_name, phone, address, state, note}` → order + Paystack init · `GET /orders/`, `/orders/<reference>/` · `POST /orders/<reference>/cancel/`.

### Safe Deal (`/api/v1/orders/`)
`GET /safe-deal/` · `POST /<reference>/safe-deal/accept/` `{delivery_service}` ·
`/tracking/` `{tracking_number}` · `/delivered/` · buyer `/confirm/` ·
`/problem/` `{reason}` · seller `/extend/`.
State machine: `paid → shipped → delivered → (confirmed | disputed)`.
Payment is held until the buyer confirms or the 24-hour window ends.

### Payments (`/api/v1/payments/`)
`GET /boost/plans/` · `POST /boost/initialize/` `{product_id, plan_id}` ·
`GET /verify/<reference>/` · `POST /webhook/` (signed HMAC-SHA512, idempotent) ·
`GET /credit/`, `/credit/transactions/`, `/referrals/` ·
`GET|POST /boost/auto-renew/`, `/pro-sales/`.

---

## 6. Media (`/api/v1/storage/media/uploads/`)

All require authentication. `POST /initiate/` accepts
`{purpose, content_type, size, filename, resume?}` and returns a polymorphic
response on `mode` (`local` | `cloudinary` | `s3` with `post`/`multipart`).
Multipart helpers: `/parts/`, `/part-url/`, `/complete/`, `/abort/`.
Full details: [ENDPOINTS.md](ENDPOINTS.md#media-uploads-skillstream-pattern).

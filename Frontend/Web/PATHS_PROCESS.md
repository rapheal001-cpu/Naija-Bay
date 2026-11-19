# NaijaBay Web — Route Process Reference

Companion to [PATHS.md](./PATHS.md). Describes what happens for each route:
session check, data fetched, and rendered outcome.

**Base:** `/` · **Auth:** JWT in HttpOnly `access` / `refresh` cookies (auth_kit).
**List pagination:** `?page=` (backend page size 20); only chat accepts
`?page_size=` (default 50, max 100).

## 1. Common process conventions

### 1.1 Session handling

- Only a user snapshot is persisted (Redux `AuthSlice` / `UserSlice` with
  redux-persist). On load, pages that need it call `useFetchUserData` /
  `fetchUserFn` (`GET /api/v1/accounts/auth/user/`) and re-sync Redux.
- There is **no** global guard component. `Profile.jsx` (and a few other
  account pages) redirect anonymous visitors to `/sign-in` in an effect.
  Actions such as favourite, chat, sell and save-search check
  `state.auth.isAuthenticated` and navigate to `/sign-in` when needed.
- Axios interceptor (`src/service/axiosInstance.js`) mirrors the readable
  `csrftoken` cookie into `X-CSRFToken` for unsafe methods, retries once on 401
  via `/api/v1/accounts/auth/token/refresh/`, clears Redux auth state if the
  refresh fails, and redirects to `/network-error` on 502.

### 1.2 Data flow

- Server state: TanStack Query hooks in `UseQuery.js`, `UseShopQuery.js` and
  `useJiji.js`. Mutations live in `UseMutation.js` and `useJiji.js`.
- Client/session state: Redux Toolkit slices in `src/slice/`.
- Request helpers: `src/service/Endpoints.js`, `ShopEndpoints.js`,
  `JijiEndpoints.js`. Media: `src/core/api/mediaApi.js`.

## 2. Public route processes

### `/` — Home

| Step | Detail |
|---|---|
| Session | Reads `isAuthenticated`; fetches current user if signed in |
| Data | `GET /products/featured/`, `GET /products/?page=1&page_size=8`, categories |
| Render | Promo bar, search hero, category strip, Trending ads, New ads, Popular searches, trust strip |

### `/products` and `/:category[/:subCategory]` — Browse

| Step | Detail |
|---|---|
| Input | Query params: `search`, `state`, `city`, `min_price`, `max_price`, `condition`, `attr_*`, `sort`, `page`; path supplies `category`/`sub_category` |
| Data | `useInfiniteProducts` with `facets=1`; attribute definitions for the active category |
| Render | Compact cards, live facet counts in sticky sidebar (xl), chips for active filters, sort and Save search |
| Actions | Filter changes rewrite the URL; infinite scroll drives `fetchNextPage` |

### `/product/detail/:product_slug` — Listing detail

| Step | Detail |
|---|---|
| Data | `GET /products/detail/<slug>/`; similar ads for market-price hint |
| Render | Gallery, price/discount, specs, description, seller card, feedback, safety tips |
| Actions | Message seller (modal), call/WhatsApp, make offer, request callback, favourite, rate, report, video upload (owner) |

### `/about`, `/safety`, `/contact`

Static content pages. `/safety` links to the profile's Safe Deal panel.

## 3. Signed-in route processes

### `/profile` and `/profile/:id`

| Step | Detail |
|---|---|
| Session | Anonymous visitors are redirected to `/sign-in` |
| Data | Current or other user profile; feedback list for that seller |
| Render | `ProfileData` plus feedback section; own profile adds Verified ID form, Seller Tools (wallet/referrals/auto-renewal/Pro Sales) and Safe Deal panel |

### `/messages`

| Step | Detail |
|---|---|
| Data | Conversations + messages via `fetchConversationsFn` / `fetchMessagesFn` |
| Transport | WebSocket `/ws/chat/<conversation_id>/` with REST fallback |
| Attachments | `uploadMediaFile` with `chat-image` / `chat-audio` purpose; returned key sent as `attachment_url` |

### `/my-ads`, `/sell`, `/product/:slug/edit`

Seller listing management. Image uploads use `uploadProductImages` →
`product-image` purpose → `POST /products/create/images/` with object keys.
Ad videos use `ad-video` purpose → `video_key`.

### `/notifications`, `/settings`, `/update-profile`, `/change-password`

Account pages using the corresponding endpoints in `Endpoints.js`.

## 4. Outcome conventions

- Backend errors use `{"code", "detail", "status", "request_id"}`; the UI shows
  safe `detail` copy and never renders stack traces or version strings.
- Mutating actions show `isPending` state and surface validation errors inline.
- Guards are UX conveniences; the backend enforces permissions on every endpoint.

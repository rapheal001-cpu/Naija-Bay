# NaijaBay Web — Route Paths Reference

Base: `/` (Vite + React Router 7). Routes are declared in `src/main.jsx` with
`createBrowserRouter`. The API base is `/api/v1/` (see `src/service/Endpoints.js`
and `src/core/constants/api.js`).

There is no central route-guard component today: pages that need a session
check do it inside the page (for example `Profile.jsx` redirects anonymous
visitors to `/sign-in`). The backend remains the final authority for 401/403.

## 1. Public routes

| Path | Page | Notes |
|---|---|---|
| `/` | `Home` | Search hero, category strip, trending/new ads, popular searches |
| `/about` | `About` | How to sell / buy, safety link |
| `/safety` | `Safety` | "Best deals are safe deals", general and per-vertical tips |
| `/contact` | `Contact` | Support |
| `/products` | `Products` | Browse/search/filter, infinite scroll, save search |
| `/:category` | `Products` | SEO category path |
| `/:category/:subCategory` | `Products` | SEO category + subcategory path |
| `/product/detail/:product_slug` | `ProductDetail` | Listing detail |
| `/sign-in` | `SignIn` | Login |
| `/register` | `Register` | Registration |
| `/email-verification-sent` | `EmailVerificationSent` | Post-signup landing |
| `/resend-email-verification` | `ResendEmailVerification` | Resend verification email |
| `/forgot-password` | `ForgotPassword` | Request reset |
| `/network-error` | `NetworkError` | Offline/network failure screen |

## 2. Signed-in routes

| Path | Page | Notes |
|---|---|---|
| `/notifications` | `Notifications` | In-app notifications |
| `/messages` | `Messages` | Conversations and chat |
| `/my-ads` | `MyAds` | Seller listings, status tabs, edit/delete |
| `/sell` | `Sell` | Post a free ad (redirects to sign-in when anonymous) |
| `/product/:product_slug/edit` | `EditProduct` | Edit own listing |
| `/profile` | `Profile` | Own profile + feedback, Verified ID, seller tools, Safe Deal |
| `/profile/:id` | `Profile` | Another user's profile + feedback |
| `/settings` | `Settings` | Account settings |
| `/update-profile` | `UpdateProfile` | Edit profile |
| `/change-password` | `ChangePassword` | Password change |

## 3. Catch-all

| Path | Page | Notes |
|---|---|---|
| `*` | `NotFound` | Branded 404 |

## 4. Path conventions

- Product URLs always use the slug: `/product/detail/<product_slug>`.
- Category browsing uses the path segments `/:category[/:subCategory]`; other
  filters (`search`, `state`, `min_price`, `attr_*`, `sort`, `page`) stay in the
  query string.
- The API base is absolute (`VITE_BASE_URL`), e.g.
  `http://localhost:8000/api/v1/products/`. Keep the hostname identical to the
  web app (`localhost`) so HttpOnly auth cookies are sent.
- The Vite dev proxy forwards `/api` to `http://localhost:8000`; it is a
  convenience and is not used while requests use `VITE_BASE_URL`.
- A 404 on a deep link in production means the static host lacks an SPA
  fallback — see [DEPLOYMENT.md](./DEPLOYMENT.md).

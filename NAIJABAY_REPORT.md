# Naija-Bay Research Report

> **Date:** 2026-11-18
> **Purpose:** Research how Jiji.ng works, inventory Naija-Bay's current features, and produce a decision menu for which features to keep, remove, or add.
> **Status:** Research only. No project code was changed.

---

## Method and evidence

- **Jiji.ng:** REA (reverse-engineering tool) launched Chrome and captured the live accessibility tree/DOM of Jiji pages. Web search returned no results, so all Jiji facts come from the live site itself.
- **Naija-Bay:** REA `inspect_sqlite_database` on `Backend/db.sqlite3` (SHA-256 `410ea5e9da3dcd1a8d7a27867e9f31e0810ee6fea8b38142c273c93b58c51491`, 1,466,368 bytes, SQLite 3.54, 46 tables, complete schema, Evidence ID `ev_5c7c7bc907d1395933a68c2992216a85e7b0ac522257471fd9d4d0ea30b554d4`). Source code was read with normal repository tools because REA is for binaries, browser pages and databases, not source code.
- **Limits:** No Jiji account was available, so logged-in seller/buyer dashboards were not observed. Some seller-side mechanics come from Jiji's own FAQ text. Your app was not launched in a browser (no server running) — a live REA capture can be added later if wanted.
- **Key Jiji evidence IDs:** homepage `ev_81b9e6f86100133163fb4a92c584bddae8dd1b1efee5e8c0bf63a8c3f7616192`; browse/filters `ev_7806c56a0e52d36e2de12ce84089b530d08d1f68a5e5331cce489931bbb4659b`; product page `ev_52504c08a116c7f1a1d605350026d46c28c93780ef6d5499ae86287bd2b5de84`; FAQ `ev_a6caf6ec328e8516b77e3ad1c674dd535a7a40cc2ce993ba5e47271218aff876`; billing policy `ev_6d6f18c6ac9946193e51dfc3e91cf09a54c30d0e319b2fcfe03a922521ed5b75`.

---

# PART 1 — How Jiji.ng works

## 1. Scale and taxonomy (observed)

Homepage shows 18 top-level categories with live ad counts:

| Category | Ads | Category | Ads |
|---|---|---|---|
| Vehicles | 364,787 | Services | 76,909 |
| Property | 104,472 | Repair & Construction | 406,403 |
| Phones & Tablets | 85,970 | Commercial Equipment & Tools | 197,960 |
| Electronics | 260,608 | Leisure & Activities | 83,881 |
| Home, Furniture & Appliances | 527,210 | Babies & Kids | 24,814 |
| Fashion | 148,642 | Food, Agriculture & Farming | 34,104 |
| Beauty & Personal Care | 80,981 | Animals & Pets | 9,571 |
| Jobs | 1,599 | Seeking Work – CVs | 17,864 |
| Business & Industry | 9,488 | | |

Each category has many subcategories (e.g. Property → rent, sale, short-let, land, commercial, event centres). URLs are location + category + slug: `/ikeja/mobile-phones/apple-iphone-12-...html`.

## 2. Buyer features (observed on browse + product pages)

- **Search + location** — "What are you looking for?" + "All Nigeria" selector.
- **Very deep filters with live counts.** On *Mobile Phones* alone: price buckets + min/max, Popular filters (NFC, 5G, AMOLED, Dual SIM, eSIM, Foldable, Gaming…), Brand (~90 brands), Condition (Brand New/Refurbished/Used), Internal Storage, RAM, Exchange Possible, Color, Number of SIMs, Display Technology, Display Size, **Bulk Price**, **Verified sellers**, **With discount**. Every option shows the number of matching ads, and there are filter-search boxes ("Find Brand", "Find Color").
- **Save filter search** — "Clear" / "Save" buttons on filters; FAQ confirms *saved searches with notifications for new ads*.
- **Favourites + follow sellers** (separate FAQ sections).
- **Seller feedback/reviews** shown under the seller name on ads, with moderation, reactions, edit, appeal, and responses to negative feedback.
- **Product page:** photo gallery (1/3 +1, view count), "Promoted" label, "X hours ago", **view counter**, breadcrumb taxonomy, long structured spec table ("Show more"), **Market price: ₦300K ~ 310K** button, **Make an offer**, **Request call back**, **Show contact**, **Start chat**, share to Facebook/Twitter/WhatsApp/email, seller card with "Verified ID", "Replies in a few hours", **18 Feedback**, "Report Abuse", "Mark unavailable", and a 5-point Safety tips box.
- **Buy Now, Pay Later** appears in listing text (down-payment offers by sellers).
- **Social login**: Google, Facebook, Apple, Truecaller (`/faq/social-login`).

## 3. Seller features (observed in FAQ + posting flow)

- **Post ad**: sign in → Sell → category, photos, title, description, fair price → Post Ad → **ad goes to moderation review** → email when live or with required edits.
- **Drafts**, photo requirements, video in ads, posting rules, prohibited items, category limits, duplicate-ad detection.
- **Managing ads**: renewal, mark as sold, moderation duration, low-priority promotion, automatic Facebook sharing, ad view statistics.
- **Seller reputation**: Verified ID badge (selfie + ID), Verified store badge (offline store), Business/Company profile, feedback system.
- **Paid promotion** (see section 5).

## 4. Trust & safety — Jiji's biggest moat: **Safe Deal** (escrow)

Observed in detail in Jiji's FAQ:

1. Buyer picks an ad with **Safe Deal**, checks item in Jiji Chat, enters delivery details, pays **through Jiji checkout**. Money is **held**, not sent to the seller.
2. Seller sees order in profile → verifies item/address/buyer note → chooses a delivery service → **Accept order** or Decline before a deadline → ships, enters **tracking number** → "Submit tracking number".
3. Or direct delivery: "I have delivered the item" → starts buyer's **24-hour confirmation window**.
4. Buyer inspects → "I've received my order". **Payment is released only after the full 24 hours**, even if the buyer confirms early, unless a problem is reported.
5. Buyer can select "There is a problem" before countdown ends → payment stays on hold → **chat with Jiji Support** → photos/evidence → support decides. Seller can "Attach proof of delivery". A dispute does not guarantee full refund or full payment.
6. Seller can extend deadline **once by 7 days**. Buyer can "Request refund" (does not instantly cancel).
7. Seller must complete **verification + payout setup** (Settings → Safe Deal) and have an active Boost Package to receive orders.

Plus: safety tips, report illegal activity, account restriction/blocking, "do not pay in advance / do not pay via chat links".

## 5. Monetization (observed — billing policy + boost FAQ)

| Product | How it works |
|---|---|
| **Boost Plans** | Lift ads across column/section/region. Non-refundable, not subscription. |
| **Boost auto-renewal** | Charged via **Paystack** bank mandate; **5% cheaper** each renewal; reminder 3 days before; price-change confirmation; cancel anytime in "My balance"; ₦50 bank verification fee refunded as Pro Sales bonus. |
| **Top Ads** | Separate block above ordinary ads. 12-month validity. |
| **Pro Sales** | **Pay-per-click** ads; only charged on clicks; pause anytime; bid groups, daily budget, campaign statistics, CTR guidance; chat reply rate and feedback affect results. |
| **Credits** | 1 Credit = ₦1, used only for premium services, expire after 12 months, forfeited on suspension. |
| **Referral Program** | Bonus per valid referral (new account + confirmed phone); credited in 24h; = ₦1 each; usable for premium services or **mobile recharge**; 12-month expiry. |
| **Jiji Balance** | Top-up, transaction history, failed-payment handling. |
| Payments accepted | Card, bank transfer, eWallet, cash at bank branch. |

Notable: **the same non-refundable policy Naija-Bay already documents.**

## 6. Other Jiji verticals (from FAQ structure)

- **Jobs & Services** — find jobs, find candidates.
- **Cars45** — sell your car via auction, inspection centres, inspection report, confidentiality.
- **Cars Inspection** — book inspection, required documents.
- **Jiji Mobile App** — download, app vs website, multiple devices.
- **Notifications** — push notification management.
- **Support** — live chat in profile, email; deliberately **no phone support** except premium callbacks.

---

# PART 2 — Naija-Bay project inventory

## Features you HAVE (keep candidates)

| Area | What exists |
|---|---|
| Auth | Email registration, verification, cookie-JWT login/logout, password change/reset, profile update, public profile, axios with credentials, `axes` lockout, CSRF/origin guards, throttle rates |
| Notifications | In-app notifications, mark one/all read, delete, unread counts |
| Stores | Create/update/delete store, logo/banner, verified flag, store detail page, followers/following, follow toggle |
| Products | Browse with category/subcategory/state/city/condition/price/search/sort/facets, **typed attribute filters**, featured, flash deals, detail by slug, create/update/delete, up to 10 images, direct-to-storage upload with fallback, My Ads, favourites, recently viewed, reports, 1–5 star ratings |
| Product extras | `original_price` discounts, negotiable, quantity, contact methods, `promoted`/`promoted_until`/`boost_level`, `delivery_available`, expiry, sold/active states |
| Chat | Conversations, messages, **WebSocket live chat + REST fallback**, image attachments, voice notes with duration, read receipts, unread counts |
| Commerce | Cart add/update/remove/clear, checkout, orders list/detail/cancel, sales list + seller status update, flat delivery fee |
| Payments | Paystack boost plans, boost initialize, order initialize, verify, **idempotent signed webhook**, payment history, dev test mode |
| Frontend | 21 pages, Redux Toolkit persisted slices + TanStack Query, Tailwind 4, infinite scroll, skeletons, error pages |
| Ops | SQLite→Postgres/Redis env switching, Cloudinary/S3, seed commands, tests, Swagger/ReDoc, production runbooks |

## Features you DON'T have (Jiji has them)

1. **Safe Deal escrow** — checkout pays immediately; no hold, tracking, 24h confirmation, dispute, or payout setup. *(Biggest gap.)*
2. **Seller feedback/reviews** — you rate *products*, not *sellers*; no moderation, reactions, edit, appeal.
3. **Verified ID / KYC** — you only have a `verified` boolean.
4. **Pro Sales PPC** — no pay-per-click, bid groups, daily budget, campaign stats.
5. **Credits wallet + referral bonuses + boost auto-renewal + Top Ads** — you have one flat boost.
6. **Saved searches with alerts**.
7. **Social login** (Google/Facebook/Apple/Truecaller).
8. **Video ads, draft ads, ad moderation queue, category ad limits, auto-renewal of listings, automatic Facebook sharing**.
9. **Make an offer / request callback / show-contact reveal / market price / buy-now-pay-later**.
10. **Block user in chat, WhatsApp contact button, support live chat**.
11. **Jobs/CVs, Cars45 auctions, car inspection services**.
12. **Mobile app** (`Frontend/Mobile/` is empty), push notifications, multi-country/locales.

## Things noticed while reading (honest findings)

- **`Backend/ENDPOINTS.md` is stale.** It documents `/register/`, `/<slug>/boost/`, `/conversations/`, but the real `urls.py` + frontend use `/registration/`, `/payments/boost/initialize/`, `/messaging/`, `/products/create/`, `/products/detail/<slug>/`. The code and frontend agree; the doc does not.
- **`README.md` itself flags a typo** in `vite.config.js` proxy: `https//localhost:8000` (unused while `VITE_BASE_URL` is set).
- Legacy string columns (`category`, `state`, `city`) still exist alongside the relational FKs — a documented deliberate contract choice, not a bug.

---

# PART 3 — Decision menu (nothing decided yet)

| # | Feature | Jiji | You | Suggested action |
|---|---|---|---|---|
| 1 | Core browse/search/filters/facets | ✅ | ✅ | **KEEP** |
| 2 | Chat + WebSocket + attachments | ✅ | ✅ | **KEEP** |
| 3 | Cart/orders/Paystack checkout + boosts | ✅ | ✅ | **KEEP** |
| 4 | Stores/follows/favourites/views/ratings/reports | ✅ | ✅ | **KEEP** |
| 5 | Auth, email verification, security stack | ✅ | ✅ | **KEEP** |
| 6 | **Safe Deal escrow** | ✅ | ❌ | **ADD if you want real trust** (largest build) |
| 7 | **Seller feedback/reviews** | ✅ | ❌ | **ADD** (medium, high trust value) |
| 8 | **Verified ID (KYC)** | ✅ | flag only | **ADD** (medium) |
| 9 | **Saved searches + alerts** | ✅ | ❌ | **ADD** (small, high engagement) |
| 10 | **Boost auto-renewal via Paystack** | ✅ | ❌ | **ADD** (small, direct revenue) |
| 11 | **Social login** | ✅ | ❌ | **ADD** (medium, acquisition) |
| 12 | Pro Sales PPC / Credits / referrals / Top Ads | ✅ | ❌ | **OPTIONAL** (complex monetization) |
| 13 | Video ads, drafts, moderation queue, ad limits | ✅ | ❌ | **OPTIONAL** (ops heavy) |
| 14 | Offer / callback / market price / BNPL | ✅ | ❌ | **OPTIONAL** |
| 15 | Jobs, Cars45, inspections | ✅ | ❌ | **SKIP unless you want a vertical** |
| 17 | Legacy string columns | partial | ✅ | **CONSIDER REMOVE** only if you accept an API breaking change |
| 18 | Stale `ENDPOINTS.md` + vite proxy typo | — | ❌ | **FIX** (documentation, not a feature) |

---

## Scope decision (operator, 2026-11-18)

- **Item #16 (mobile app / push notifications / multi-country) is removed from scope.** No mobile, push, or multi-country work will be done. The row was removed from the decision menu above.
- Work is proceeding from **backend → frontend web** to redesign the web app to closely match Jiji.ng, using REA-captured Jiji pages as the reference.

---

## Implementation log — Jiji-style web redesign (started 2026-11-18)

### Additional REA captures used as design reference
| Page | Evidence ID | What it showed |
|---|---|---|
| Sell (redirects to login) | `ev_7fc620861d7e5e66bba37af6cefd42397e322af33db311033472b72a8c247617` | Sell requires sign-in |
| Seller store page | `ev_c01ded7b24f9b0a4e588152f1188eb3ec2c6c8c69295834f3f5e80da1448c5e8` | "3+ years on Jiji", Verified ID, Last seen, Feedback (18), ads-by-category tabs, ratings on cards |
| Real-estate browse | `ev_544d24101bdb809f3a8dba240422289da5519da2ec4234a2ba1b4facecf86f28` | Category sidebar with counts, price buckets, popular bedroom-filter links |
| Apple brand page | `ev_81ee276b4d851f0a8634f328ec56bab3c359a2c77e270d055440a96383fd1eee` | Attribute filters + related-model links with counts |
| About | `ev_3b34be3c7134e5b4379bd994d30f971c4d0bdee50c9836c507d55c8b8c8953b4` | "Jiji is the best place to sell anything to real people", How to sell/buy, safety, pro selling |
| Safety tips | `ev_091037045b87f72223aa2971f8315a09051d832f2997d2a43086dee94845fa42` | "Best deals are safe deals", general + vertical-specific tips |

Jiji rendering pattern applied: header tagline + search + location + Sell; breadcrumb; category sidebar with live counts; compact cards with tier badge (VIP/PREMIUM/DIAMOND/ENTERPRISE), rating, location, age; detail page with market-price hint, seller card and 5-point safety list.

### Backend changes
- `Backend/products/serializers.py` — added three **read-only, derived** fields (no migration required):
  - `badge`: VIP / PREMIUM / DIAMOND / ENTERPRISE, derived from `promoted` and `boost_level`.
  - `posted_ago`: human-readable age ("2 hours ago", "3 days ago", …).
  - `location_label`: `"city, state"` string.

### Frontend changes
- `ProductCard.jsx` — rewritten as a compact Jiji-style ad card with tier badge, price, rating, seller/store line, location and age.
- `Search.jsx` — hero copy now Jiji-style ("Search thousands of ads from sellers all over Nigeria", placeholder "I am looking for...").
- `Home.jsx` — "Trending ads" / "New ads" sections, plus a "Popular searches" category link block.
- `Header.jsx` — Jiji utility strip: "Sell faster , Buy smarter", About/Help, EN.
- `Product.jsx` — market-price hint estimated from similar ads, Jiji-style 5-point safety tips block.
- `Products.jsx` — breadcrumb (Home / Category / Subcategory / Nigeria), denser 5-column grid on wide screens.

### Verification
- `python -m py_compile products/serializers.py` — pass.
- `python manage.py check` — 0 issues.
- Serializer smoke test returned `{'badge': None, 'posted_ago': '10 days ago', 'location_label': 'lafiagi, kwara', ...}`.
- `npm run build` — pass.
- `npm run lint` — 0 errors (5 pre-existing React Hook Form warnings).

### Not yet done (next slices)
- Permanent left sidebar filters with counts on browse (Jiji layout) — current filters are a collapsible panel.
- Seller feedback/reviews system, Safe Deal escrow, Verified ID KYC, saved searches, boost auto-renewal, social login, About/Safety content pages.


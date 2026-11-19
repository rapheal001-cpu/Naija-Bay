# NaijaBay Frontend

The frontend is the web marketplace experience for NaijaBay — a Nigerian
classifieds marketplace styled after Jiji.ng (free ads, categories, seller
trust) with Temu-like deals and discounts. Buyers browse, search, favourite,
rate and chat with sellers; sellers post free ads, promote them with Paystack
boosts, and manage their store.

For the product story and architecture, read [../UNDERSTAND.md](../UNDERSTAND.md).
For backend routes see [../Backend/ENDPOINTS.md](../Backend/ENDPOINTS.md).

## Clients in this folder

| Client | Location | Stack | Status |
|---|---|---|---|
| Web | [`Web/`](./Web/) | React 19, Vite 8, React Router 7, Redux Toolkit + Persist, TanStack Query 5, Axios, Tailwind CSS 4 | Shipped client — `npm run dev` |
| Mobile | `Mobile/` | — | Out of scope (empty folder) |

## Web client quick start

```powershell
cd Web
npm install
npm run dev
```

Vite serves `http://localhost:5173`. The React app calls the Django API at the
absolute URL in `Web/.env` (`VITE_BASE_URL=http://localhost:8000`). Use the same
hostname (`localhost`) for both apps so the cookie-based JWT session is sent;
mixing `localhost` and `127.0.0.1` makes the browser treat them as different sites.

Build and lint: `npm run build`, `npm run lint`.

## What the web client includes

- Jiji-style home: search hero, category strip, trending/new ads, popular searches.
- Browse with live facet counts, a sticky filter sidebar on wide screens, sort,
  save-search, and infinite scrolling.
- Compact ad cards with tier badges (VIP/PREMIUM/DIAMOND/ENTERPRISE), ratings,
  location, view counts and relative age.
- Product detail with gallery, specs, market-price hint, make-offer and
  callback requests, seller feedback, safety tips, and ad-video upload for owners.
- Cart, Paystack checkout, order history, Safe Deal escrow actions, and payments.
- Seller tools: credits wallet, referrals, boost auto-renewal and Pro Sales campaigns.
- Verified ID (KYC) submission, seller feedback with moderation, and follows.
- Real-time chat over WebSockets with a REST fallback; image/voice attachments.
- Account flows (register, verify, login, profile, settings, password reset),
  notifications, About and Safety pages.

## Media and uploads

The client asks the backend how to upload, then follows the returned mode:

| Backend mode | What the web client does |
|---|---|
| `local` | Sends the File through the normal model create/update endpoint |
| `cloudinary` | POSTs the file directly to Cloudinary using server-signed fields |
| `s3` + `strategy: post` | POSTs the file straight to S3 with a presigned form |
| `s3` + `strategy: multipart` | Uploads 10 MB parts (resumable via IndexedDB), then completes |

Purposes keep uploads scoped: `product-image`, `ad-video`, `chat-image`,
`chat-audio`, `verification-selfie`, `verification-document`, `store-logo`,
`store-banner`, `user-avatar`. Limits: 2 MB images, 100 MB videos. Credentials
stay on the backend — never put Cloudinary/AWS secrets in a `VITE_*` variable.
See [Web/DEVELOPMENT.md](./Web/DEVELOPMENT.md#media-and-uploads).

## Documentation

- [Web README](./Web/README.md) — stack, structure, feature overview
- [Web Development](./Web/DEVELOPMENT.md) — local setup and conventions
- [Web Deployment](./Web/DEPLOYMENT.md) — build, hosting, SPA fallback
- [Route paths](./Web/PATHS.md) and [route process](./Web/PATHS_PROCESS.md)

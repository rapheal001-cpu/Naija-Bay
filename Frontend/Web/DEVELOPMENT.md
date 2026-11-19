# NaijaBay Web — Development Guide

## Requirements

- Node.js 20+ and npm (Vite 8).
- The NaijaBay Django API. Start it with Daphne/ASGI so WebSockets work:
  `python -m daphne -p 8000 NaijaBay.asgi:application`, or use
  `python run_server.py` from `Backend/`.

## Install and run

```powershell
npm install
npm run dev
```

Vite serves `http://localhost:5173`. The client calls the API at the absolute
URL in `.env`:

```env
VITE_BASE_URL=http://localhost:8000
```

Use `localhost` for both apps so the HttpOnly auth cookies are same-site.
The `vite.config.js` proxy forwards `/api` to `http://localhost:8000` as a
convenience; requests made through `axiosInstance` use `VITE_BASE_URL`.

## Scripts

| Command | Purpose |
|---|---|
| `npm run dev` | Vite dev server on 5173 |
| `npm run build` | Production build into `dist/` |
| `npm run lint` | ESLint over the project |
| `npm run preview` | Serve the production build locally |

Current status: `npm run build` passes; `npm run lint` reports 0 errors and 5
pre-existing React Hook Form `incompatible-library` warnings. No frontend test
runner is configured.

## Project structure

```text
src/
  main.jsx              router + providers (QueryClient, Redux, PersistGate)
  store.js              Redux store
  core/
    api/                mediaApi.js, resumableUploads.js
    constants/api.js    media endpoint paths + upload purposes
    utils/uploadImages.js
  service/              axiosInstance.js, Endpoints.js, ShopEndpoints.js, JijiEndpoints.js
  hooks/                UseQuery.js, UseMutation.js, UseShopQuery.js, useJiji.js
  slice/                Auth, User, Product, Category, Notification, Store
  components/
    HeaderComponents/   header, search, category nav, mobile bottom nav
    ProductComponents/  cards, forms, ratings, report/chat modals
    JijiComponents/     feedback, offers, Verified ID, seller tools, Safe Deal, video
    ShopComponents/     cart/checkout UI
    UserComponents/     profile UI
  pages/                route-level screens
  skeletons/            loading placeholders
  style.css             Tailwind entry + global styles
```

## Conventions

- Add backend calls in `src/service/*`, wrap them with TanStack Query in
  `src/hooks/*`, then consume the hook in a page.
- Build mobile-first: one column on phones, then `sm`/`lg`/`2xl` breakpoints.
  Browse uses a sticky 280px filter sidebar at `xl` and a collapsible panel below.
- Use `min-w-0` on flex children and `truncate`/`break-words` for long titles.
- Account-only actions must check `isAuthenticated` and redirect to `/sign-in`.
- Media uploads always go through `uploadMediaFile(file, purpose)`. Do not
  inline Cloudinary/S3 calls in components.

## Media and uploads

`src/core/api/mediaApi.js` calls
`POST /api/v1/storage/media/uploads/initiate/` with a purpose and file metadata.
The backend answers with a mode:

| Mode | Client behaviour |
|---|---|
| `local` | Return the `File`; the normal multipart create/update endpoint stores it |
| `cloudinary` | POST directly with server-signed fields; return `{key, url}` |
| `s3` + `post` | POST directly with a presigned form; return the key |
| `s3` + `multipart` | Upload 10 MB parts via `part-url`, reconcile with `parts`, then `complete`; sessions are stored in IndexedDB (`resumableUploads.js`) |

Purposes must match `NaijaBay.media.UPLOAD_PURPOSES`. Uploaded object keys are
attached to domain endpoints (`image_key`, `video_key`, `selfie_key`,
`document_key`, `attachment_url`) and validated for ownership server-side.

Limits: 2 MB images, 100 MB videos. Never add AWS/Cloudinary credentials to a
`VITE_*` variable — Vite inlines those into the public bundle.

## Backend connection

See `Backend/ENDPOINTS.md` for routes and `Backend/ENDPOINTS_PROCESS.md` for
request/response examples. Keep `.env` out of git.

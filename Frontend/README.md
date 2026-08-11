# NaijaBay Frontend

The frontend is the marketplace experience for the NaijaBay project. It is built with React, Vite, Tailwind CSS, Redux Toolkit, Redux Persist, and TanStack Query. The app connects to the Django REST API in the backend and presents the marketplace pages in a clean, responsive way.

## What the frontend does

The frontend currently supports:

- home feed and featured product browsing
- product detail views with seller and pricing context
- category and product search flows
- user authentication with sign-in and registration
- seller listing flows for posting a product
- profile, update profile, business detail, notifications, and message views
- favorites and protected navigation

## Tech stack

- React 19
- Vite 8
- React Router DOM
- TanStack Query for server data caching and mutations
- Redux Toolkit + Redux Persist for auth, user, product, category, and notification state
- Tailwind CSS for layout and styling
- Axios for HTTP requests

## Frontend project structure

```text
Frontend/
├── src/
│   ├── assets/
│   ├── components/         # Reusable UI pieces, headers, auth forms, product cards, and shared UI
│   ├── hooks/              # React Query hooks for fetching and mutating data
│   ├── pages/              # Route-level screens
│   ├── service/            # Backend endpoint helpers and Axios wiring
│   ├── slice/              # Redux slices for auth, products, categories, notifications, and user data
│   ├── skeletons/         # Loading placeholders for list/detail views
│   └── style.css           # Global styles and Tailwind entry
├── .env                    # Environment variables for backend connection
├── package.json            # Frontend scripts and dependencies
└── vite.config.js          # Vite dev server and API proxy configuration
```

## How it works

1. The app boots through the `main.jsx` router.
2. Route-level screens are mounted from the `pages/` folder.
3. The Redux store keeps auth and user context durable using Redux Persist.
4. TanStack Query handles remote data reads and mutations.
5. `axiosInstance.js` centralizes the API base URL, credentials, and timeout handling.
6. `Endpoints.js` maps frontend operations to the Django backend paths.

## Backend connection

The frontend uses a single environment entry for backend connectivity:

```env
VITE_BASE_URL=http://127.0.0.1:8000
```

For Ngrok testing, set the same public backend URL in the frontend `.env` file and mirror it in the backend `.env` file as well. The Vite config reads this value and uses it for the `/api` proxy target during development.

All requests are then appended with backend paths such as:

- `/api/v1/accounts/auth/login`
- `/api/v1/accounts/auth/registration`
- `/api/v1/accounts/auth/user`
- `/api/v1/products`
- `/api/v1/products/create`
- `/api/v1/products/create/images`
- `/api/v1/products/detail/<slug>`

### How to connect a new backend endpoint

If the backend adds a new route, the usual flow is:

1. Add the request function in `src/service/Endpoints.js`.
2. Create or update a React Query hook in `src/hooks/UseMutation.js` or `src/hooks/UseQuery.js`.
3. Import the hook inside the page or component that needs the UI action.
4. Use the mutation result in `mutate`, `mutateAsync`, or `isPending` to render loading and error feedback.

Example pattern:

```js
export const myNewEndpointFn = async (payload) => {
  const { data } = await axiosInstance.post("/api/v1/...", payload);
  return data;
};
```

## Authentication and protected flows

Authentication is managed in Redux and mirrored to the backend session cookies through `withCredentials: true` in the Axios instance.

Protected flows such as:

- posting an ad
- viewing private profile state
- favorites and notifications
- protected account/profile updates

depend on the signed-in user state in Redux and the `isAuthenticated` flag.

## Production-readiness notes

The frontend is laid out to be production-friendly and can be prepared for deployment by:

- keeping API routes in one service layer
- using TanStack Query for cached server state
- storing persistent auth/user state with Redux Persist
- using environment variables for backend host selection
- keeping route-level screens isolated in `src/pages/`

For a final production build, run the following command from the `Frontend/` folder after the backend is available and all required environment values are set:

```bash
npm run build
```

## Running the frontend locally

```bash
cd Frontend
npm install
npm run dev
```

The dev server exposes the app through Vite. The `/api/v1/...` traffic is sent to the backend URL configured in `.env`, and the Vite proxy is configured to route those requests to the backend target.

## Notes for contributors

- Keep API requests inside the service layer.
- Keep route pages in `src/pages/`.
- Use the existing query and mutation hooks instead of calling React Query directly inside plain helper functions.
- Keep the backend URL in `.env` rather than hardcoding it into components.
- If you change the backend host for testing, update the frontend and backend env files together and restart the relevant dev servers.

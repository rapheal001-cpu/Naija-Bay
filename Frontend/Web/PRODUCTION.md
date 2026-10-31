# NaijaBay Production Deployment Guide

This guide explains how to move the NaijaBay backend and frontend into production in a way that works reliably. The backend and frontend are separate services, so they should be deployed separately even though they are part of the same product.

## Why the backend and frontend are deployed separately

The backend is an API server. It handles:

- authentication and sessions
- database operations
- file uploads
- business logic
- protected endpoints

The frontend is a client application. It handles:

- page rendering
- user experience
- client-side state
- API calls to the backend

Because they have different responsibilities, they are usually hosted differently:

- the backend needs a runtime environment, a database, environment variables, and background process support
- the frontend mostly needs a static host or server that can serve the built app

That is why production deployments usually look like this:

- Frontend host: Vercel, Netlify, Cloudflare Pages, AWS S3 + CloudFront, or similar
- Backend host: Render, Railway, Fly.io, AWS Elastic Beanstalk, AWS ECS, AWS EC2, or similar

---

## Recommended production architecture

### Option A: Simple and beginner-friendly

- Backend: Render or Railway
- Frontend: Vercel
- Database: PostgreSQL on Render / Railway / Neon / Supabase

This is the easiest path for most small and medium projects.

### Option B: AWS-style production setup

- Backend: AWS EC2, Elastic Beanstalk, or ECS
- Frontend: S3 + CloudFront or Amplify
- Database: RDS PostgreSQL

This is more flexible and enterprise-friendly, but more complex to set up.

### Option C: Full-platform managed deployment

- Backend: Railway or Render
- Frontend: Netlify or Vercel
- Storage: S3 or Cloudflare R2 for media files

This gives a good balance of simplicity, speed, and extensibility.

---

## Backend production deployment

### 1. Prepare the Django backend

Before deployment, make sure the backend is ready for production:

- set `DEBUG=False`
- set `ENVIRONMENT=production`
- use a strong `SECRET_KEY`
- set `ALLOWED_HOSTS` to your deployed backend domain
- set `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS` to the frontend domain and any API domain you use
- use PostgreSQL instead of SQLite
- configure static and media storage

### 2. Backend environment variables

The backend should receive these environment variables in production:

```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-very-secure-secret-key
ALLOWED_HOSTS=your-backend-domain.com
CSRF_TRUSTED_ORIGINS=https://your-frontend-domain.com,https://your-backend-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
SITE_ID=1
TIME_ZONE=Africa/Lagos
LANGUAGE_CODE=en-us
DATABASE_URL=postgresql://user:password@host:5432/dbname
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@your-domain.com
```

### 3. Backend hosting options

#### Render

Good for:

- small to medium apps
- fast setup
- simple database integration

Typical setup:

- build command: `pip install -r requirements.txt`
- start command: `gunicorn NaijaBay.wsgi:application`
- add a PostgreSQL database
- add environment variables from your `.env`

#### Railway

Good for:

- fast deployments
- simple environment management
- easy database provisioning

Typical setup:

- connect the repo
- set the build/start command
- attach PostgreSQL
- add environment variables

#### AWS

Good for:

- large apps
- high control and scalability
- enterprise-grade infrastructure

Typical setup:

- Elastic Beanstalk, ECS, or EC2
- RDS PostgreSQL
- S3 for media storage if needed
- load balancer and domain configuration if required

### 4. Backend production build considerations

The backend should run with a production WSGI server such as Gunicorn. The project should also collect static files during deployment.

Typical commands:

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

---

## Frontend production deployment

### 1. Prepare the React frontend

Before deployment, the frontend should be built with Vite:

```bash
cd Frontend
npm install
npm run build
```

That produces a production-ready static bundle.

### 2. Frontend environment variables

The frontend should receive a production API URL such as:

```env
VITE_BASE_URL=https://your-backend-domain.com
```

This value should be the public URL of the deployed backend, not the local development URL.

### 3. Frontend hosting options

#### Vercel

Good for:

- React and Vite applications
- automatic deployments from GitHub
- simple custom domain support

Typical setup:

- connect the repo
- select the Frontend folder as the app root
- add the `VITE_BASE_URL` environment variable
- deploy

#### Netlify

Good for:

- static frontend deployment
- simple CI/CD from GitHub
- custom domains and redirects

#### Cloudflare Pages

Good for:

- fast global delivery
- cheap static hosting
- modern edge deployment

#### AWS

Good for:

- full control
- enterprise hosting
- static delivery through S3 + CloudFront

---

## Important production configuration notes

### CORS

The backend must allow the frontend origin in production.

Example:

```env
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### CSRF

If your app uses cookies or forms, the backend must also trust the frontend domain.

Example:

```env
CSRF_TRUSTED_ORIGINS=https://your-frontend-domain.com
```

### Cookies

If authentication relies on cookies, you must ensure:

- the frontend and backend share the same top-level domain or a properly configured CORS setup
- the cookie settings are compatible with HTTPS
- the backend is served over HTTPS

### Media files

If users upload images, you should not rely only on local disk storage in production. Consider:

- S3
- Cloudflare R2
- other object storage providers

---

## Recommended deployment path for this project

For this project, the most practical production setup is:

- Backend: Render or Railway with PostgreSQL
- Frontend: Vercel
- Media storage: S3 or Cloudflare R2 if file uploads need to persist in production

That combination is easy to maintain and gives a good balance of stability and speed.

---

## Example deployment flow

### Backend

1. Create a new service on Render or Railway
2. Connect the repository
3. Set the backend folder as the app root
4. Add environment variables
5. Attach PostgreSQL
6. Deploy

### Frontend

1. Create a new project on Vercel or Netlify
2. Connect the repository
3. Set the frontend folder as the app root
4. Add the production backend URL in `VITE_BASE_URL`
5. Deploy

---

## Final recommendation

If you want the easiest path to production:

- deploy the backend on Render or Railway
- deploy the frontend on Vercel
- use PostgreSQL for the database
- store uploaded media in S3 or Cloudflare R2 if needed

That setup is a strong production choice for this app because it is simple, reliable, and scalable without requiring a lot of infrastructure maintenance.

# NaijaBay Deployment Checklist

This file is a practical step-by-step checklist for deploying the NaijaBay backend and frontend to production.

## 1. Prepare the backend

- Set `DEBUG=False`
- Set `ENVIRONMENT=production`
- Generate a strong `SECRET_KEY`
- Set `ALLOWED_HOSTS` to your production backend domain
- Set `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS` for your frontend domain
- Switch from SQLite to PostgreSQL
- Configure static and media storage

## 2. Backend environment variables

Add these values in your hosting platform:

```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-very-secure-secret-key
ALLOWED_HOSTS=your-backend-domain.com
CSRF_TRUSTED_ORIGINS=https://your-frontend-domain.com,https://your-backend-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

## 3. Backend deployment steps

### Render

1. Create a new Render web service
2. Connect your GitHub repository
3. Choose the backend folder as the app root
4. Set the build command to:

```bash
pip install -r requirements.txt
```

5. Set the start command to:

```bash
gunicorn NaijaBay.wsgi:application
```

6. Add PostgreSQL and environment variables
7. Deploy

### Railway

1. Create a new Railway project
2. Connect the repository
3. Add the backend service
4. Set the runtime command
5. Add PostgreSQL
6. Add environment variables
7. Deploy

## 4. Prepare the frontend

- Run the production build locally:

```bash
cd Frontend
npm install
npm run build
```

- Make sure the frontend uses the deployed backend URL in production:

```env
VITE_BASE_URL=https://your-backend-domain.com
```

## 5. Frontend deployment steps

### Vercel

1. Create a new Vercel project
2. Import the repository
3. Set the app root to the frontend folder
4. Add the `VITE_BASE_URL` environment variable
5. Deploy

### Netlify

1. Create a new Netlify site
2. Import the repository
3. Set the frontend folder as the site root
4. Add the production API URL as an environment variable
5. Deploy

## 6. Post-deployment checks

- Test login and registration
- Test product creation and listing
- Test image uploads
- Test notifications and profile updates
- Confirm the frontend can reach the backend over HTTPS
- Confirm CORS and CSRF are working
- Confirm the app works on mobile and desktop

## 7. Recommended simple production setup

For this project, the easiest production configuration is:

- Backend: Render or Railway
- Frontend: Vercel
- Database: PostgreSQL
- Media storage: S3 or Cloudflare R2 if needed

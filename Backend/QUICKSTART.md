# NaijaBay Backend Quickstart

This guide is the fastest way to run the NaijaBay Django API locally or through a public tunnel.

## 1. Open the backend folder

```bash
cd C:\Users\HP\OneDrive\Desktop\Projects\NaijaBay\Backend
```

## 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure the environment

A `.env` file already exists in the backend folder for local development. Confirm that it contains the values required for your machine, especially:

```env
ENVIRONMENT=development
SECRET_KEY=django-insecure-dev-only-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,your-ngrok-host
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://your-ngrok-host
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://your-ngrok-host
SITE_ID=1
TIME_ZONE=Africa/Lagos
LANGUAGE_CODE=en-us
```

If you are using Ngrok, make sure the public host you expose matches the value in both the backend env file and the frontend env file.

## 5. Run database migrations

```bash
py manage.py migrate
```

## 6. Start the API server

```bash
py manage.py runserver 0.0.0.0:8000
```

The backend will be available from:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/api/v1/docs/`
- `https://your-ngrok-host` if you have a public tunnel running

## 7. Validate the current backend flow

Once the server is running, confirm these areas work:

- registration and email verification
- login/logout with cookie-based auth
- current user profile fetch and update
- product list and detail endpoints
- category listing
- product creation and image upload
- favorite toggling
- notifications fetch and mark-all-read

## 8. Helpful commands

```bash
py manage.py makemigrations
py manage.py migrate
py manage.py createsuperuser
py manage.py collectstatic --noinput
py manage.py test
py manage.py check
```

## 9. Notes

- This project uses auth_kit for auth endpoints and JWT cookie authentication.
- The frontend should target the backend through the origin configured in its own `.env` file.
- The `Backend/.env` file is the source of local runtime configuration for the Django service.
- After changing `.env` values, restart Django so the updated CORS/CSRF host lists are loaded.

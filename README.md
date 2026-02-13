# HKSD Speech Platform

Full-stack project with:
- `backend/` Django + Django REST Framework API and admin
- `frontend/` Vite + React client

## 1. Prerequisites

- Python 3.13 (recommended for local parity with deploy)
- Node.js 20+ and npm
- Git

## 2. Environment variables

Copy the example file at repo root:

```bash
cp .env.example .env
```

Set values in `.env`:

```env
DJANGO_SECRET_KEY=replace-with-a-secure-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=
FRONTEND_BASE_URL=http://127.0.0.1:5173
DJANGO_SETTINGS_MODULE=config.settings.dev
```

Notes:
- For local development, leave `DATABASE_URL` empty to use SQLite.
- `DJANGO_SETTINGS_MODULE=config.settings.dev` is for local development.
- `FRONTEND_BASE_URL` is used to build password reset links.

## 3. Backend local setup (`backend/`)

### Create and activate virtual environment

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

This project keeps only direct runtime dependencies in `backend/requirements.txt`.

### Run migrations and create admin user

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Start backend server

```bash
python manage.py runserver
```

Backend URLs:
- API root: `http://127.0.0.1:8000/api/`
- Admin: `http://127.0.0.1:8000/admin/`

## 4. Frontend local setup (`frontend/`)

The Vite dev server proxies `/api` to Django (`http://127.0.0.1:8000`), so no CORS setup is needed for local dev.

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:
- `http://127.0.0.1:5173/` (or the URL shown by Vite)

## 5. Running both services together

Use two terminals:

Terminal 1:
```bash
cd backend
source .venv/bin/activate
python manage.py runserver
```

Terminal 2:
```bash
cd frontend
npm run dev
```

## 6. Useful development commands

Backend checks:

```bash
cd backend
source .venv/bin/activate
python manage.py check
python manage.py makemigrations --check --dry-run
```

Frontend production build:

```bash
cd frontend
npm run build
```

## 7. Python version for Heroku

- This repo uses `.python-version` at the project root.
- Current value: `3.13`.
- Heroku recommends major-version pinning in `.python-version` so patch security updates are picked up automatically during builds.

## 8. Production/deployment note (Heroku)

- `Procfile` is included with:
  - `release: cd backend && python manage.py migrate`
  - `web: cd backend && gunicorn config.wsgi:application`
- In production, set `DJANGO_SETTINGS_MODULE=config.settings.prod`.
- Ensure `DATABASE_URL` is set to your Heroku Postgres URL.
- Production app URL: `https://hksd-speech-platform-385f3de9d301.herokuapp.com/`
- Recommended production env values:
  - `DJANGO_ALLOWED_HOSTS=hksd-speech-platform-385f3de9d301.herokuapp.com`
  - `FRONTEND_BASE_URL=https://hksd-speech-platform-385f3de9d301.herokuapp.com`
  - `DJANGO_DEBUG=False`

Debug mode on Heroku:
- Keep `DJANGO_DEBUG=False` by default.
- To temporarily enable debug for troubleshooting:
  - `heroku config:set DJANGO_DEBUG=True`
- To disable it again:
  - `heroku config:set DJANGO_DEBUG=False`

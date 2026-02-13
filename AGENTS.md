# AGENTS Guide

## Persistent User Preferences
- Use British English in comments, documentation, and assistant outputs.
- Follow PEP 8.
- Do not code defensively.
- Add a module docstring at the top of each Python script, and keep it updated when the script changes.

## Project Layout
- Backend: `backend/` (Django + DRF)
- Frontend: `frontend/` (Vite + React)

## Heroku Deployment Facts
- Accessible Heroku app for current account: `hksd-speech-platform` (region: EU).
- Git remote URL: `https://git.heroku.com/hksd-speech-platform.git`
- Root-level Python dependency shim exists: `requirements.txt` includes `-r backend/requirements.txt`.

## Heroku Build and Runtime Requirements
- Buildpacks must be set in this order:
  1. `heroku/nodejs`
  2. `heroku/python`
- Root `package.json` contains `heroku-postbuild` to build frontend assets:
  - `npm --prefix frontend ci`
  - `npm --prefix frontend run build`
- `Procfile` release phase runs:
  - `cd backend && python manage.py migrate && python manage.py collectstatic --noinput`
- `Procfile` web phase runs:
  - `cd backend && gunicorn config.wsgi:application`

## Django Production Behaviour
- On Heroku (`DYNO` present), defaults now select `config.settings.prod` in:
  - `backend/manage.py`
  - `backend/config/wsgi.py`
  - `backend/config/asgi.py`
- Production `ALLOWED_HOSTS` always includes:
  - `hksd-speech-platform-385f3de9d301.herokuapp.com`
- `FRONTEND_BASE_URL` in production defaults to:
  - `https://hksd-speech-platform-385f3de9d301.herokuapp.com`
- `DJANGO_DEBUG` in production is env-driven and should be kept `False` unless temporarily troubleshooting.

## Static and Frontend Serving
- WhiteNoise is enabled in Django middleware.
- Static files use `CompressedManifestStaticFilesStorage`.
- Frontend built assets are expected under:
  - `frontend/dist/`
  - `frontend/dist/assets/`
- If `frontend/dist/index.html` is missing at runtime, `/` falls back to a plain backend response (`HKSD Speech Platform API`).

## Recommended Heroku Config Vars
- `DJANGO_SETTINGS_MODULE=config.settings.prod`
- `DJANGO_ALLOWED_HOSTS=hksd-speech-platform-385f3de9d301.herokuapp.com`
- `FRONTEND_BASE_URL=https://hksd-speech-platform-385f3de9d301.herokuapp.com`
- `DJANGO_DEBUG=False`
- `DATABASE_URL=<Heroku Postgres URL>`

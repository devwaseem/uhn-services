# UHN Services

## Quickstart

### 1) Create env file

```
cp env_template.txt .env
```

### 2) Install dependencies

```
uv sync --dev
npm install
```

### 3) Run dev server

```
export DJANGO_SETTINGS_MODULE=app.settings.dev
uv run --env-file .env python manage.py runserver
```

`.env` is loaded in local commands via `uv run --env-file .env`.

### 4) Run frontend

```
npm run dev
```

## Settings Modules

- Development: `app.settings.dev`
- Production: `app.settings.prod`
- Test: `app.settings.test`

## Common Commands (Just)

- `just dev`
- `just vite`
- `just test`
- `just lint`
- `just typecheck`
- `just migrate`
- `just docs`

## Healthcheck

If enabled (`ENABLE_HEALTH_CHECK=true`), the endpoint is available at:

```
/healthz/
```

Readiness checks are available at:

```
/readyz/
```

## Documentation

```bash
uv run mkdocs serve
```

## Notes

- Set `SECRET_KEY` to a secure random value for production.
- Set `ALLOWED_HOSTS` for production.
- Run `uv run --env-file .env python manage.py check --deploy` before shipping.

## Static & Media

- Local/Whitenoise: set `STATIC_USE_WHITENOISE=true`, run `collectstatic`
- S3: set `STATIC_USE_S3=true` and/or `MEDIA_USE_S3=true` with AWS creds

# Deployment

## Production Checklist

- Set `SECRET_KEY`, `ALLOWED_HOSTS`, and `USE_SSL=true`
- Provide `CSRF_TRUSTED_ORIGINS`
- Run (local/dev): `uv run --env-file .env python manage.py check --deploy`
- Run (production): `python manage.py check --deploy` with env vars provided by your platform

## Static & Media Strategy

### Local/Whitenoise

- Set `STATIC_USE_WHITENOISE=true`
- Run `uv run --env-file .env python manage.py collectstatic` for local/dev workflows

## Environment Loading

- `.env` is not auto-loaded by plain `python manage.py ...` commands.
- For local development, prefer `uv run --env-file .env ...`.
- In production, inject environment variables through your runtime/orchestrator.

### S3-backed

- Set `STATIC_USE_S3=true` and/or `MEDIA_USE_S3=true`
- Provide `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_REGION_NAME`

## Reverse Proxy

Enable these for proxy deployments:

- `USE_SSL=true`
- `USE_X_FORWARDED_HOST=true`

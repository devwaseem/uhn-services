# Settings

## Modules
- Development: `app.settings.dev`
- Production: `app.settings.prod`
- Test: `app.settings.test`

## Required Production Values
Set these before deployment:
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `USE_SSL=true`

## Runtime Protections
Production defaults are controlled via:
- `SECURE_REFERRER_POLICY`
- `SECURE_CROSS_ORIGIN_OPENER_POLICY`
- `SECURE_CROSS_ORIGIN_EMBEDDER_POLICY`
- `SECURE_CROSS_ORIGIN_RESOURCE_POLICY`

## Static and Media
- `DJANGO_STATIC_HOST` and `DJANGO_MEDIA_HOST` control URL prefixes.
- `STATIC_LOCATION` controls where collected static files are stored.
  - Recommended default for local/dev: `static`
  - Typical production path: `/var/www/static`
- `STATIC_USE_WHITENOISE=true` enables local serving via Whitenoise.
- `STATIC_USE_S3=true` and/or `MEDIA_USE_S3=true` switches to S3-backed storage.

## OpenTelemetry
Key OTEL settings:
- `ENABLE_OTEL`
- `OTEL_SDK_DISABLED`
- `OTEL_SERVICE_NAME`
- `OTEL_SERVICE_NAMESPACE`
- `OTEL_EXPORTER_OTLP_ENDPOINT`
- `OTEL_EXPORTER_OTLP_PROTOCOL`
- `OTEL_EXPORTER_OTLP_HEADERS`
- `OTEL_TRACES_SAMPLER`
- `OTEL_TRACES_SAMPLER_ARG`
- `OTEL_METRIC_EXPORT_INTERVAL`
- `OTEL_PYTHON_DJANGO_EXCLUDED_URLS`

## CSP
The project uses Django’s built-in CSP with nonces in production and a relaxed
policy in development for Vite.

- `CSP_EXCLUDE_PATH_PREFIXES` controls paths that should not emit CSP headers
  (defaults to `['/admin']`).

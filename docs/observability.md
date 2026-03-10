# Observability

## Health Endpoints
When `ENABLE_HEALTH_CHECK=true`:
- `/healthz/` runs full health checks
- `/readyz/` runs readiness checks (db/cache/redis)

## OpenTelemetry
Enable OTEL with:
- `ENABLE_OTEL=true`
- `OTEL_SDK_DISABLED=false`
- `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318`

Core runtime instrumentation:
- Django HTTP server spans
- Celery producer/worker spans
- Redis and Psycopg spans
- Trace-aware structured logs

## Structured Logging
Request logging is enabled via `django-structlog`.

- Development (`app.settings.dev`) uses `plain_console` for human-readable logs.
- Production (`app.settings.prod`) enforces JSON output via `json_console`.
- Production startup fails if any logger uses `plain_console`.

Trace correlation fields:
- `trace_id`
- `span_id`

## Local Collector
Collector config location:
- `observability/otel-collector.yaml`

Run the collector with your preferred container tooling and point
`OTEL_EXPORTER_OTLP_ENDPOINT` to it.

## Sentry
Set `ENABLE_SENTRY=true` and `SENTRY_DSN` to enable Sentry in production.

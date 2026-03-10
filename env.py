from pathlib import Path

import environ

BASE_DIR = Path(__file__).parent

environ.Env.read_env(BASE_DIR / ".env", overwrite=True)

Env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    TEST=(bool, False),
    ACCOUNT_ALLOW_REGISTRATION=(bool, True),
    SITE_ID=(int, 1),
    REDIS_PORT=(int, 6379),
    DJANGO_DATABASE_PORT=(int, 5432),
    CONN_MAX_AGE=(int, 60),
    EMAIL_BACKEND=(str, "django.core.mail.backends.smtp.EmailBackend"),
    EMAIL_PORT=(int, 1025),
    EMAIL_USE_TLS=(bool, False),
    NO_CACHE=(bool, False),
    LOG_DB=(bool, False),
    DISABLE_LOGGING=(bool, False),
    ENABLE_HEALTH_CHECK=(bool, False),
    ENABLE_SILK_PROFILING=(bool, False),
    ENABLE_CPROFILE=(bool, False),
    ENABLE_PYINSTRUMENT=(bool, False),
    ENABLE_SENTRY=(bool, False),
    ENABLE_OTEL=(bool, False),
    OTEL_SDK_DISABLED=(bool, False),
    OTEL_SERVICE_NAME=(str, "uhn_services"),
    OTEL_SERVICE_NAMESPACE=(str, "uhn_services"),
    OTEL_RESOURCE_ATTRIBUTES=(str, ""),
    OTEL_EXPORTER_OTLP_ENDPOINT=(str, "http://localhost:4318"),
    OTEL_EXPORTER_OTLP_PROTOCOL=(str, "http/protobuf"),
    OTEL_EXPORTER_OTLP_HEADERS=(str, ""),
    OTEL_EXPORTER_OTLP_TIMEOUT=(int, 30),
    OTEL_TRACES_SAMPLER=(str, "parentbased_traceidratio"),
    OTEL_TRACES_SAMPLER_ARG=(float, 0.1),
    OTEL_METRIC_EXPORT_INTERVAL=(int, 60000),
    OTEL_PYTHON_DJANGO_EXCLUDED_URLS=(str, "healthz/,readyz/"),
    # security
    USE_SSL=(bool | None, None),
    USE_X_FORWARDED_HOST=(bool, False),
    # static
    VITE_APP_OUTPUT_DIR=(str, "dist"),
    STATIC_USE_WHITENOISE=(bool, False),
    DJANGO_STATIC_HOST=(str, ""),
    DJANGO_MEDIA_HOST=(str, ""),
    MEDIA_USE_S3=(bool, False),
    STATIC_USE_S3=(bool, False),
)

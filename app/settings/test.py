from __future__ import annotations

from typing import Any

from . import base as base_settings


def _copy_base_settings() -> dict[str, Any]:
    return {
        name: value
        for name, value in vars(base_settings).items()
        if name.isupper()
    }


globals().update(_copy_base_settings())

DEBUG = False
TEST = True
DJFK_DEV_ENV = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

ENABLE_HEALTH_CHECK = False
ENABLE_SILK_PROFILING = False
ENABLE_CPROFILE = False
ENABLE_PYINSTRUMENT = False
ENABLE_SENTRY = False
ENABLE_OTEL = False
OTEL_SDK_DISABLED = True

INSTALLED_APPS = [
    app
    for app in base_settings.INSTALLED_APPS
    if app
    not in {
        "health_check",
        "health_check.db",
        "health_check.cache",
        "health_check.storage",
        "health_check.contrib.migrations",
        "health_check.contrib.celery",
        "health_check.contrib.celery_ping",
        "health_check.contrib.psutil",
        "health_check.contrib.s3boto3_storage",
        "health_check.contrib.redis",
        "silk",
    }
]

MIDDLEWARE = [
    middleware
    for middleware in base_settings.MIDDLEWARE
    if middleware
    not in {
        "silk.middleware.SilkyMiddleware",
        "django_cprofile_middleware.middleware.ProfilerMiddleware",
        "pyinstrument.middleware.ProfilerMiddleware",
    }
]

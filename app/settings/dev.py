from __future__ import annotations

import logging
from typing import Any, cast

import structlog

from app.telemetry import add_trace_context_to_event
from env import Env

from . import base as base_settings


def _copy_base_settings() -> dict[str, Any]:
    return {
        name: value
        for name, value in vars(base_settings).items()
        if name.isupper()
    }


globals().update(_copy_base_settings())

DEBUG = True

ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS = [
    *base_settings.INSTALLED_APPS,
    "django_browser_reload",
    "debug_toolbar",
    "nplusone.ext.django",
    "django_extensions",
]

MIDDLEWARE = [
    "nplusone.ext.django.NPlusOneMiddleware",
    *base_settings.MIDDLEWARE,
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "debug_toolbar.middleware.show_toolbar",
}

NPLUSONE_LOGGER = structlog.getLogger("django")
NPLUSONE_LOG_LEVEL = logging.WARNING
NPLUSONE_WHITELIST = [{"model": "admin.LogEntry", "field": "user"}]

SECURE_CSP = {
    directive: list(values)
    for directive, values in base_settings.SECURE_CSP.items()
}

# Dev CSP: allow Vite dev server runtime
vite_origin = base_settings.VITE_DEV_SERVER_ORIGIN
vite_ws = f"ws://{base_settings.VITE_DEV_SERVER_HOST}:{base_settings.VITE_DEV_SERVER_PORT}"
SECURE_CSP["script-src"].append(vite_origin)
if base_settings.CSP.NONCE in SECURE_CSP["style-src"]:
    SECURE_CSP["style-src"].remove(base_settings.CSP.NONCE)
SECURE_CSP["style-src"].extend([vite_origin, base_settings.CSP.UNSAFE_INLINE])
SECURE_CSP["connect-src"].extend([vite_origin, vite_ws])

LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
            "foreign_pre_chain": [
                structlog.contextvars.merge_contextvars,
                add_trace_context_to_event,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.ExceptionPrettyPrinter(),
            ],
        },
        "console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.KeyValueRenderer(
                key_order=["timestamp", "level", "event", "logger"],
            ),
            "foreign_pre_chain": [
                structlog.contextvars.merge_contextvars,
                add_trace_context_to_event,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.ExceptionPrettyPrinter(),
            ],
        },
    },
    "handlers": {
        "plain_console": {
            "class": "logging.StreamHandler",
            "formatter": "plain_console",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "loggers": {
        "django_structlog": {
            "handlers": ["plain_console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "werkzeug": {
            "handlers": ["plain_console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["plain_console"],
            "propagate": True,
            "level": "DEBUG",
        },
        "django.server": {
            "handlers": ["plain_console"],
            "propagate": False,
            "level": "DEBUG",
        },
        "django.core.cache": {
            "handlers": ["plain_console"],
            "propagate": False,
            "level": "DEBUG",
        },
        "django.template": {
            "handlers": ["plain_console"],
            "propagate": False,
            "level": "INFO",
        },
        "django.security": {
            "handlers": ["plain_console"],
            "level": "WARNING",
            "propagate": False,
        },
        "celery": {
            "handlers": ["plain_console"],
            "level": "INFO",
            "propagate": False,
        },
        "app": {
            "handlers": ["plain_console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

if Env.bool("LOG_DB"):
    cast(dict[str, Any], LOGGING["loggers"])["django.db"] = {
        "handlers": ["plain_console"],
        "propagate": False,
        "level": "DEBUG",
    }


DJFK_DEV_ENV = True

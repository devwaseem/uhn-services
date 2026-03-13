from __future__ import annotations

from typing import Any, cast

from django.core.exceptions import ImproperlyConfigured

from env import Env

from . import base as base_settings


def _copy_base_settings() -> dict[str, Any]:
    return {
        name: value
        for name, value in vars(base_settings).items()
        if name.isupper()
    }


globals().update(_copy_base_settings())

DEBUG = False
ALLOWED_HOSTS = list(base_settings.ALLOWED_HOSTS)
SECRET_KEY = base_settings.SECRET_KEY
USE_SSL = base_settings.USE_SSL

if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("ALLOWED_HOSTS must be set in production.")

if not SECRET_KEY or SECRET_KEY == "replace-me":
    raise ImproperlyConfigured("SECRET_KEY must be set to a secure value.")

USE_X_FORWARDED_HOST = Env.bool("USE_X_FORWARDED_HOST")
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https" if USE_SSL else "http",
)

SECURE_HSTS_SECONDS = 63072000  # 2 years
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_REFERRER_POLICY = Env.str(
    "SECURE_REFERRER_POLICY",
    default="strict-origin-when-cross-origin",
)
SECURE_CROSS_ORIGIN_OPENER_POLICY = Env.str(
    "SECURE_CROSS_ORIGIN_OPENER_POLICY",
    default="same-origin",
)
SECURE_CROSS_ORIGIN_EMBEDDER_POLICY = Env.str(
    "SECURE_CROSS_ORIGIN_EMBEDDER_POLICY",
    default="credentialless",
)
SECURE_CROSS_ORIGIN_RESOURCE_POLICY = Env.str(
    "SECURE_CROSS_ORIGIN_RESOURCE_POLICY",
    default="same-site",
)

LOGGING = base_settings.LOGGING
LOGGING["handlers"]["json_console"]["formatter"] = "json"

for logger_name, logger_config in cast(
    dict[str, dict[str, Any]],
    LOGGING["loggers"],
).items():
    handlers = cast(list[str], logger_config.get("handlers", []))
    if "plain_console" in handlers:
        raise ImproperlyConfigured(
            f"Logger {logger_name} cannot use plain_console in production."
        )

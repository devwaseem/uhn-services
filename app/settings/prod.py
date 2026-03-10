from __future__ import annotations

from django.core.exceptions import ImproperlyConfigured

from env import Env

from .base import *  # noqa: F403

DEBUG = False

if not ALLOWED_HOSTS:  # noqa: F405
    raise ImproperlyConfigured("ALLOWED_HOSTS must be set in production.")

if not SECRET_KEY or SECRET_KEY == "replace-me":  # noqa: F405
    raise ImproperlyConfigured("SECRET_KEY must be set to a secure value.")

USE_X_FORWARDED_HOST = Env.bool("USE_X_FORWARDED_HOST")
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https" if USE_SSL else "http",  # noqa: F405
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

LOGGING["handlers"]["json_console"]["formatter"] = "json"  # noqa: F405

for logger_name, logger_config in LOGGING["loggers"].items():  # noqa: F405
    if "plain_console" in logger_config.get("handlers", []):
        raise ImproperlyConfigured(
            f"Logger {logger_name} cannot use plain_console in production."
        )

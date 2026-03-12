from __future__ import annotations

import os
from collections.abc import Iterable
from typing import Final, cast, overload

from django.core.exceptions import ImproperlyConfigured

_TRUE_VALUES: Final = frozenset({"1", "true", "t", "yes", "y", "on"})
_FALSE_VALUES: Final = frozenset({"0", "false", "f", "no", "n", "off"})


class _Env:
    def __init__(self, **schema: tuple[object, object]) -> None:
        self._defaults = {
            key: default_value for key, (_, default_value) in schema.items()
        }

    def _raw(self, var: str, default: object | None = None) -> object | None:
        env_value = os.getenv(var)
        if env_value is not None:
            return env_value

        if default is not None:
            return default

        if var in self._defaults:
            return self._defaults[var]

        msg = f"Set the {var} environment variable"
        raise ImproperlyConfigured(msg)

    @overload
    def str(self, var: str) -> str:
        ...

    @overload
    def str(self, var: str, default: str) -> str:
        ...

    def str(self, var: str, default: str | None = None) -> str:
        value = self._raw(var, default)
        if value is None:
            msg = f"{var} must be a string"
            raise ImproperlyConfigured(msg)
        return str(value)

    @overload
    def int(self, var: str) -> int:
        ...

    @overload
    def int(self, var: str, default: int) -> int:
        ...

    def int(self, var: str, default: int | None = None) -> int:
        value = self._raw(var, default)
        if value is None:
            msg = f"{var} must be an integer"
            raise ImproperlyConfigured(msg)
        if isinstance(value, int):
            return value

        try:
            return int(str(value).strip())
        except ValueError as exc:
            msg = f"{var} must be an integer"
            raise ImproperlyConfigured(msg) from exc

    @overload
    def float(self, var: str) -> float:
        ...

    @overload
    def float(self, var: str, default: float) -> float:
        ...

    def float(self, var: str, default: float | None = None) -> float:
        value = self._raw(var, default)
        if value is None:
            msg = f"{var} must be a float"
            raise ImproperlyConfigured(msg)
        if isinstance(value, float):
            return value

        try:
            return float(str(value).strip())
        except ValueError as exc:
            msg = f"{var} must be a float"
            raise ImproperlyConfigured(msg) from exc

    @overload
    def bool(self, var: str) -> bool:
        ...

    @overload
    def bool(self, var: str, default: bool) -> bool:
        ...

    def bool(self, var: str, default: bool | None = None) -> bool:
        value = self._raw(var, default)
        if value is None:
            msg = f"{var} must be a boolean value"
            raise ImproperlyConfigured(msg)
        if isinstance(value, bool):
            return value

        lowered = str(value).strip().lower()
        if lowered in _TRUE_VALUES:
            return True
        if lowered in _FALSE_VALUES:
            return False

        msg = (
            f"{var} must be a boolean value (true/false, yes/no, on/off, 1/0)"
        )
        raise ImproperlyConfigured(msg)

    def list(
        self,
        var: str,
        default: list[str] | None = None,
    ) -> list[str]:
        value = self._raw(var, default)
        if value is None:
            return []

        if isinstance(value, str):
            return [
                item
                for item in (segment.strip() for segment in value.split(","))
                if item
            ]

        if isinstance(value, Iterable):
            items: list[str] = []
            iterable_value = cast(Iterable[object], value)
            for item in iterable_value:
                text = str(item).strip()
                if text:
                    items.append(text)
            return items

        text = str(value).strip()
        if not text:
            return []
        return [text]


Env = _Env(
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
    USE_SSL=(bool, False),
    USE_X_FORWARDED_HOST=(bool, False),
    # static
    VITE_APP_OUTPUT_DIR=(str, "dist"),
    STATIC_USE_WHITENOISE=(bool, False),
    DJANGO_STATIC_HOST=(str, ""),
    DJANGO_MEDIA_HOST=(str, ""),
    MEDIA_USE_S3=(bool, False),
    STATIC_USE_S3=(bool, False),
)

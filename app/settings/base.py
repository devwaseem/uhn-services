from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, Protocol, cast

import django_stubs_ext
import structlog
from django.contrib.messages import constants as messages
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from storages.backends.s3boto3 import S3Boto3Storage

from app.helpers.network import get_ip_from_request
from app.telemetry import add_trace_context_to_event
from env import Env


class _CSPValues(Protocol):
    SELF: str
    NONCE: str
    UNSAFE_INLINE: str


_FALLBACK_CSP = SimpleNamespace(
    SELF="'self'",
    NONCE="'nonce-{nonce}'",
    UNSAFE_INLINE="'unsafe-inline'",
)


def _load_csp() -> _CSPValues:
    try:
        csp_module = importlib.import_module("django.utils.csp")
    except ModuleNotFoundError:
        return cast(_CSPValues, _FALLBACK_CSP)

    return cast(_CSPValues, getattr(csp_module, "CSP", _FALLBACK_CSP))


CSP = _load_csp()

if TYPE_CHECKING:
    from celery.app.task import Task

    Task.__class_getitem__ = classmethod(lambda cls, *args, **kwargs: cls)  # type: ignore[attr-defined] # noqa

django_stubs_ext.monkeypatch()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DEBUG = Env.bool("DEBUG")
TEST = "test" in sys.argv or sys.argv[0].endswith("pytest") or Env.bool("TEST")

SECRET_KEY = Env.str("SECRET_KEY")

NO_CACHE = Env.bool("NO_CACHE")

REDIS_HOST = Env.str("REDIS_HOST")
REDIS_PORT = Env.str("REDIS_PORT")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

ENABLE_HEALTH_CHECK = Env.bool("ENABLE_HEALTH_CHECK")
ENABLE_SILK_PROFILING = Env.bool("ENABLE_SILK_PROFILING")
ENABLE_CPROFILE = Env.bool("ENABLE_CPROFILE")
ENABLE_PYINSTRUMENT = Env.bool("ENABLE_PYINSTRUMENT")
ENABLE_SENTRY = Env.bool("ENABLE_SENTRY")
ENABLE_OTEL = Env.bool("ENABLE_OTEL")

OTEL_SDK_DISABLED = Env.bool("OTEL_SDK_DISABLED")
OTEL_SERVICE_NAME = Env.str("OTEL_SERVICE_NAME")
OTEL_SERVICE_NAMESPACE = Env.str("OTEL_SERVICE_NAMESPACE")
OTEL_RESOURCE_ATTRIBUTES = Env.str("OTEL_RESOURCE_ATTRIBUTES")
OTEL_EXPORTER_OTLP_ENDPOINT = Env.str("OTEL_EXPORTER_OTLP_ENDPOINT")
OTEL_EXPORTER_OTLP_PROTOCOL = Env.str("OTEL_EXPORTER_OTLP_PROTOCOL")
OTEL_EXPORTER_OTLP_HEADERS = Env.str("OTEL_EXPORTER_OTLP_HEADERS")
OTEL_EXPORTER_OTLP_TIMEOUT = Env.int("OTEL_EXPORTER_OTLP_TIMEOUT")
OTEL_TRACES_SAMPLER = Env.str("OTEL_TRACES_SAMPLER")
OTEL_TRACES_SAMPLER_ARG = Env.float("OTEL_TRACES_SAMPLER_ARG")
OTEL_METRIC_EXPORT_INTERVAL = Env.int("OTEL_METRIC_EXPORT_INTERVAL")
OTEL_PYTHON_DJANGO_EXCLUDED_URLS = Env.str("OTEL_PYTHON_DJANGO_EXCLUDED_URLS")

STATIC_USE_WHITENOISE = Env.bool("STATIC_USE_WHITENOISE")
STATIC_USE_S3 = Env.bool("STATIC_USE_S3")
MEDIA_USE_S3 = Env.bool("MEDIA_USE_S3")

# Security
USE_SSL = Env.bool("USE_SSL")
ALLOWED_HOSTS = Env.list("ALLOWED_HOSTS", [])
INTERNAL_IPS: list[str] = []

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

# session
SESSION_COOKIE_SECURE = USE_SSL
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = Env.list("CSRF_TRUSTED_ORIGINS", [])

# csrf
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = USE_SSL
CSRF_COOKIE_SAMESITE = "Lax"

SECURE_SSL_REDIRECT = USE_SSL

# https://github.com/adamchainz/django-permissions-policy#setting
PERMISSIONS_POLICY: dict[str, str | list[str]] = {}

# Application definition

ADMIN_APPS = [
    "admin_interface",
    "colorfield",
    # "unfold",  # before django.contrib.admin
    # "unfold.contrib.filters",  # optional, if special filters are needed
    # "unfold.contrib.forms",  # optional, if special form elements are needed
    # "unfold.contrib.inlines",  # optional, if special inlines are needed
    "django.contrib.admin",
]

DEFAULT_DJANGO_APPS: list[str] = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sites",
    "django.contrib.sitemaps",
]

THIRD_PARTY_APPS: list[str] = [
    "frontend_kit",
    "storages",
    "django_cotton",
    "constance",
    "django_structlog",
    "django_object_actions",  # https://github.com/crccheck/django-object-actions
    "solo",  # https://github.com/lazybird/django-solo
    "widget_tweaks",  # django-widget-tweaks
    "phonenumber_field",
]

PROJECT_APPS: list[str] = [
    "app.apps.Config",
]

ALL_AUTH_APPS: list[str] = [
    "allauth",
    "allauth.account",
]

INSTALLED_APPS = [
    *ADMIN_APPS,
    *DEFAULT_DJANGO_APPS,
    *THIRD_PARTY_APPS,
    *PROJECT_APPS,
    *ALL_AUTH_APPS,
]

MIDDLEWARE: list[str] = [
    # Logging:
    # "app.middleware.disable_client_side_caching_middleware", # Uncomment this line to disable client side caching # noqa
    # "django.middleware.cache.UpdateCacheMiddleware",  # This must be first on the list # noqa
    "django_structlog.middlewares.RequestMiddleware",
    "app.middleware.csp_excluder",
    # Content Security Policy:
    "django.middleware.csp.ContentSecurityPolicyMiddleware",
    # Django:
    "django.middleware.security.SecurityMiddleware",
    # django-permissions-policy
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Django HTMX
    "django_htmx.middleware.HtmxMiddleware",
    # "django.middleware.cache.FetchFromCacheMiddleware",  # This must be last
]

if STATIC_USE_WHITENOISE:
    MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "app.urls"

# Templates

DJFK_FRONTEND_DIR = BASE_DIR / "frontend"
DJFK_DEV_ENV = False

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            # Contains plain text templates, like `robots.txt`:
            BASE_DIR / "app" / "templates",
            DJFK_FRONTEND_DIR,
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Default template context processors:
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                # Django CSP
                "django.template.context_processors.csp",
                # Custom
                "app.context_processors.get_site_data",
                "app.context_processors.allauth_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "app.wsgi.application"
ASGI_APPLICATION = "app.asgi.application"

APPEND_SLASH = True

# Internationalization

LANGUAGE_CODE = "en-us"

USE_TZ = True

TIME_ZONE = "UTC"

LANGUAGES = (("en", _("English")),)

USE_I18N = False

USE_L10N = True

DATE_INPUT_FORMATS = ("%d-%m-%Y", "%Y-%m-%d")

# https://django-phonenumber-field.readthedocs.io/en/latest/reference.html#phonenumber-default-region
PHONENUMBER_DEFAULT_REGION = "US"  # Defaults to India

# Messages
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"
MESSAGE_TAGS = {
    messages.DEBUG: "gray",
    messages.INFO: "blue",
    messages.SUCCESS: "green",
    messages.WARNING: "yellow",
    messages.ERROR: "red",
}

# Authentication
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

AUTH_USER_MODEL = "app.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = Env.int("SITE_ID", default=1)

LOGIN_URL = reverse_lazy("account_login")
LOGIN_REDIRECT_URL = "/"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",  # noqa
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",  # noqa
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",  # noqa
    },
]

# Session
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# Allauth
CUSTOM_ALLAUTH_CONFIG_PATH = "app.allauth"
ACCOUNT_ADAPTER = CUSTOM_ALLAUTH_CONFIG_PATH + ".adapter.AllAuthAccountAdapter"
ACCOUNT_FORMS = {
    "signup": CUSTOM_ALLAUTH_CONFIG_PATH + ".forms.SignupForm",
    "reset_password": CUSTOM_ALLAUTH_CONFIG_PATH + ".forms.ResetPasswordForm",
}
ACCOUNT_ALLOW_REGISTRATION = Env.bool("ACCOUNT_ALLOW_REGISTRATION")
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_USER_MODEL_USERNAME_FIELD: str | None = None
ACCOUNT_LOGOUT_REDIRECT_URL = reverse_lazy("account_login")

# Database
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES: dict[str, dict[str, Any]] = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": Env.str("POSTGRES_DB"),
        "USER": Env.str("POSTGRES_USER"),
        "PASSWORD": Env.str("POSTGRES_PASSWORD"),
        "HOST": Env.str("DJANGO_DATABASE_HOST"),
        "PORT": Env.int("DJANGO_DATABASE_PORT"),
        "CONN_MAX_AGE": Env.int("CONN_MAX_AGE"),
        "OPTIONS": {
            "connect_timeout": 10,
            "options": "-c statement_timeout=15000ms",
        },
    },
}

if TEST:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }

# Caching
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    },
}

if TEST or NO_CACHE:
    CACHES["default"] = {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache"
    }

# Vite
VITE_OUTPUT_DIR = Env.str("VITE_OUTPUT_DIR", "./dist")
VITE_DEV_SERVER_HOST = "localhost"
VITE_DEV_SERVER_PORT = 5173
VITE_DEV_SERVER_ORIGIN = (
    f"http://{VITE_DEV_SERVER_HOST}:{VITE_DEV_SERVER_PORT}"
)
VITE_DEV_SERVER_URL = f"{VITE_DEV_SERVER_ORIGIN}/"

# AWS / S3
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_DEFAULT_ACL: str | None = None
AWS_S3_FILE_OVERWRITE = True
AWS_S3_VERIFY = True
AWS_QUERYSTRING_AUTH = False
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_LOCATION = "media"
AWS_ACCESS_KEY_ID = Env.str("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = Env.str("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = Env.str("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_S3_REGION_NAME = Env.str("AWS_S3_REGION_NAME")
AWS_S3_HOST = f"{AWS_S3_REGION_NAME}.amazonaws.com"


class StaticStorage(S3Boto3Storage):  # type: ignore
    location = "static"
    default_acl = None


class PublicMediaStorage(S3Boto3Storage):  # type: ignore
    location = "media"
    default_acl = None
    file_overwrite = False


class DBBackupStorage(S3Boto3Storage):  # type: ignore
    location = "db-backups"
    default_acl = None
    file_overwrite = False


DJANGO_STATIC_HOST = Env.str("DJANGO_STATIC_HOST")
DJANGO_MEDIA_HOST = Env.str("DJANGO_MEDIA_HOST")

_media_location = "media"
_static_location = Env.str(
    "STATIC_LOCATION",
    "static" if DEBUG else "/var/www/static",
)
_media_url = f"{DJANGO_MEDIA_HOST}/media/"
_static_url = f"{DJANGO_STATIC_HOST}/static/"

_default_storage_backend = "django.core.files.storage.FileSystemStorage"
_default_storage_options: dict[str, str] = {
    "location": _media_location,
    "base_url": _media_url,
}

_staticfiles_storage_backend = (
    "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
)
_staticfiles_storage_options: dict[str, str] = {
    "location": _static_location,
    "base_url": _static_url,
}

if STATIC_USE_WHITENOISE:
    _staticfiles_storage_backend = (
        "whitenoise.storage.CompressedManifestStaticFilesStorage"
    )

    def immutable_file_test(_: object, url: str) -> Any:
        # Match filename with 12 hex digits before the extension
        # e.g. app.db8f2edc0c8a.js
        import re

        return re.match(r"^.+\.\w+\..+$", url)

    WHITENOISE_IMMUTABLE_FILE_TEST = immutable_file_test

if MEDIA_USE_S3:
    _media_url = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
    _default_storage_backend = "app.settings.base.PublicMediaStorage"
    _default_storage_options = {
        "location": _media_location,
    }

if STATIC_USE_S3:
    _static_location = "static"
    _static_url = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    _staticfiles_storage_backend = "app.settings.base.StaticStorage"
    _staticfiles_storage_options = {
        "location": _static_location,
    }

MEDIA_LOCATION = _media_location
STATIC_LOCATION = _static_location
MEDIA_URL = _media_url
STATIC_URL = _static_url

STORAGES: dict[str, dict[str, Any]] = {
    "default": {
        "BACKEND": _default_storage_backend,
        "OPTIONS": _default_storage_options,
    },
    "staticfiles": {
        "BACKEND": _staticfiles_storage_backend,
        "OPTIONS": _staticfiles_storage_options,
    },
}


STATIC_ROOT = cast(str, STORAGES["staticfiles"]["OPTIONS"]["location"])

STATICFILES_DIRS = [VITE_OUTPUT_DIR]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# CSP (Django built-in)
CSP_EXCLUDE_PATH_PREFIXES = ["/admin", "/api/docs"]

SECURE_CSP: dict[str, list[str]] = {
    "default-src": [CSP.SELF],
    "script-src": [
        CSP.SELF,
        CSP.NONCE,
        "https://cdn.jsdelivr.net/",
    ],
    "style-src": [
        CSP.SELF,
        CSP.NONCE,
        "https://fonts.googleapis.com",
    ],
    "font-src": [CSP.SELF, "https://fonts.gstatic.com", "data:"],
    "img-src": [CSP.SELF, "data:", "https:"],
    "connect-src": [CSP.SELF],
    "media-src": [CSP.SELF, "data:"],
}

if STATIC_URL.startswith("http"):
    for directive in (
        "script-src",
        "style-src",
        "font-src",
        "img-src",
        "connect-src",
        "media-src",
    ):
        SECURE_CSP[directive].append(STATIC_URL)

if MEDIA_URL.startswith("http"):
    for directive in ("img-src", "media-src", "connect-src"):
        SECURE_CSP[directive].append(MEDIA_URL)

# Emails
EMAIL_TIMEOUT = 5
SERVER_EMAIL = Env.str(
    "SERVER_EMAIL",
    default="<system@uhn_services>",
)
DEFAULT_FROM_EMAIL = Env.str(
    "DEFAULT_FROM_EMAIL",
    "<no-reply@uhn_services>",
)

EMAIL_BACKEND = Env.str(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = Env.str("EMAIL_HOST")
EMAIL_HOST_USER = Env.str("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = Env.str("EMAIL_HOST_PASSWORD")
EMAIL_PORT = Env.int("EMAIL_PORT")
EMAIL_USE_TLS = Env.bool("EMAIL_USE_TLS")


# Logging
LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
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
    },
    "handlers": {
        "json_console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django_structlog": {
            "handlers": ["json_console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "gunicorn": {
            "handlers": ["json_console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.server": {
            "handlers": ["json_console", "mail_admins"],
            "propagate": True,
            "level": "INFO",
        },
        "django.security": {
            "handlers": ["json_console", "mail_admins"],
            "level": "WARNING",
            "propagate": True,
        },
        "celery": {
            "handlers": ["json_console", "mail_admins"],
            "level": "INFO",
            "propagate": True,
        },
        "app": {
            "handlers": ["json_console", "mail_admins"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

if Env.bool("LOG_DB"):
    cast(dict[str, Any], LOGGING["loggers"])["django.db"] = {
        "handlers": ["json_console"],
        "propagate": False,
        "level": "DEBUG",
    }

# Constance
CONSTANCE_CONFIG: dict[str, Any] = {}

# Rate limiting
RATELIMIT_HASH_ALGORITHM = "hashlib.md5"


def RATELIMIT_IP_META_KEY(request: HttpRequest) -> str | None:  # noqa
    return get_ip_from_request(request=request)


# Optional integrations
if ENABLE_HEALTH_CHECK:
    INSTALLED_APPS.extend(
        [
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
        ]
    )

    HEALTH_CHECK = {
        "DISK_USAGE_MAX": 90,
        "MEMORY_MIN": 100,
    }

    HEALTHCHECK_CACHE_KEY = "health_check"
    CACHES[HEALTHCHECK_CACHE_KEY] = {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/3",
    }

if ENABLE_SILK_PROFILING:
    INSTALLED_APPS.append("silk")
    MIDDLEWARE.append("silk.middleware.SilkyMiddleware")
    SILKY_PYTHON_PROFILER = True

if ENABLE_CPROFILE:
    MIDDLEWARE.append(
        "django_cprofile_middleware.middleware.ProfilerMiddleware"
    )
    DJANGO_CPROFILE_MIDDLEWARE_REQUIRE_STAFF = True

if ENABLE_PYINSTRUMENT:
    MIDDLEWARE.append("pyinstrument.middleware.ProfilerMiddleware")
    SECURE_CSP["script-src"].append(CSP.UNSAFE_INLINE)

if ENABLE_SENTRY:
    import sentry_sdk

    sentry_dsn = Env.str("SENTRY_DSN")

    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=Env.float("SENTRY_TRACES_SAMPLE_RATE", 0.0),
        )

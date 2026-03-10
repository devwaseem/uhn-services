"""
ASGI config for the project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os

from django.core.asgi import get_asgi_application

from app.telemetry import initialize_telemetry

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "app.settings.dev",
)

initialize_telemetry()

application = get_asgi_application()

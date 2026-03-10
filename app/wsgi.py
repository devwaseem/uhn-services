"""
WSGI config for the project

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os

from django.core.wsgi import get_wsgi_application

from app.telemetry import initialize_telemetry

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "app.settings.dev",
)

initialize_telemetry()

application = get_wsgi_application()

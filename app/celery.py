import logging.config
import os
from typing import Any

import django
from celery import Celery, signals
from celery.app.task import Task
from celery.signals import worker_process_init
from django.conf import settings
from django_structlog.celery.steps import DjangoStructLogInitStep

from app.telemetry import initialize_telemetry

Task.__class_getitem__ = classmethod(lambda cls, *args, **kwargs: cls)  # type: ignore[attr-defined] # noqa

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "app.settings.dev",
)

django.setup()
initialize_telemetry(service_name="uhn_services-worker")

app = Celery("uhn_services")
app.config_from_object("app.celeryconfig")

app.steps["worker"].add(DjangoStructLogInitStep)

packages = [
    "app.flow_extension.tasks",
]

app.autodiscover_tasks(packages=packages)


@signals.setup_logging.connect
def setup_celery_logging(**_kwargs: Any) -> None:
    logging.config.dictConfig(settings.LOGGING)


@app.on_after_configure.connect
def setup_periodic_tasks(_sender: Any, **_kwargs: Any) -> None: ...


@worker_process_init.connect(weak=False)
def setup_worker_process_telemetry(*_args: Any, **_kwargs: Any) -> None:
    initialize_telemetry(service_name="uhn_services-worker")

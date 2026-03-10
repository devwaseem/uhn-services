from __future__ import annotations

import os
import socket
from collections.abc import MutableMapping
from typing import Any

from django.conf import settings
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span

_INITIALIZED = False
_INITIALIZED_PID = -1


def otel_enabled() -> bool:
    if getattr(settings, "TEST", False):
        return False
    if getattr(settings, "ENABLE_OTEL", False) is not True:
        return False
    return not getattr(settings, "OTEL_SDK_DISABLED", False)


def initialize_telemetry(service_name: str | None = None) -> None:
    global _INITIALIZED
    global _INITIALIZED_PID

    current_pid = os.getpid()
    if _INITIALIZED and current_pid == _INITIALIZED_PID:
        return

    if not otel_enabled():
        return

    resource = Resource.create(
        {
            "service.name": service_name
            or str(
                getattr(
                    settings,
                    "OTEL_SERVICE_NAME",
                    "uhn_services",
                )
            ),
            "service.namespace": str(
                getattr(settings, "OTEL_SERVICE_NAMESPACE", "app")
            ),
            "service.instance.id": socket.gethostname(),
            "deployment.environment": _deployment_environment(),
        }
    )

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(),
        export_interval_millis=int(
            getattr(settings, "OTEL_METRIC_EXPORT_INTERVAL", 60000)
        ),
    )
    meter_provider = MeterProvider(
        resource=resource, metric_readers=[metric_reader]
    )
    metrics.set_meter_provider(meter_provider)

    LoggingInstrumentor().instrument(set_logging_format=False)
    DjangoInstrumentor().instrument()
    CeleryInstrumentor().instrument()
    RedisInstrumentor().instrument()
    PsycopgInstrumentor().instrument()

    _INITIALIZED = True
    _INITIALIZED_PID = current_pid


def current_trace_ids() -> dict[str, str]:
    span = trace.get_current_span()
    trace_id, span_id = _trace_ids_from_span(span)
    return {
        "trace_id": trace_id,
        "span_id": span_id,
    }


def add_trace_context_to_event(
    _logger: Any,
    _name: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    trace_context = current_trace_ids()
    event_dict["trace_id"] = trace_context["trace_id"]
    event_dict["span_id"] = trace_context["span_id"]
    return event_dict


def _trace_ids_from_span(span: Span) -> tuple[str, str]:
    context = span.get_span_context()
    if not context.is_valid:
        return "", ""
    return (
        format(context.trace_id, "032x"),
        format(context.span_id, "016x"),
    )


def _deployment_environment() -> str:
    settings_module = str(os.getenv("DJANGO_SETTINGS_MODULE", ""))
    if settings_module.endswith(".prod"):
        return "production"
    if settings_module.endswith(".test"):
        return "test"
    return "development"

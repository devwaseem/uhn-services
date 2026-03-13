import shutil
import tempfile
from typing import Any, Callable, NamedTuple
from uuid import uuid4

import structlog
from celery import Task

from app.celery import app
from app.flow_extension.credential import INVOICE_FLOW_EXTENSION_CREDENTIAL
from app.flow_extension.exceptions import FlowExtensionRateLimitError
from app.flow_extension.models import (
    FlowExtensionHandlerActionResult,
    FlowExtensionHandlerNextAction,
)
from app.flow_extension.repository import (
    FlowExtensionEventRepository,
    get_pending_flow_extension_events,
)
from app.solutions.ship_to_detection.tasks import verify_ship_to_address

logger = structlog.get_logger(__name__)


FlowExtensionHandler = Callable[..., FlowExtensionHandlerActionResult]


@app.task(
    autoretry_for=(FlowExtensionRateLimitError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_backoff_max=60 * 60,  # 60 minutes
)
def check_and_handle_invoice_from_flow_extension() -> None:
    current_logger = logger.bind(reference=str(uuid4()))
    current_logger.info("Checking flow extension for Invoice based events")
    new_events = get_pending_flow_extension_events(
        credential=INVOICE_FLOW_EXTENSION_CREDENTIAL,
    )
    current_logger.info(
        "Got %d events",
        len(new_events),
        new_events=new_events,
    )

    for event in new_events:
        event_repo = FlowExtensionEventRepository(
            event_id=event.event_id,
            credential=INVOICE_FLOW_EXTENSION_CREDENTIAL,
        )
        handle_flow_extension_event.delay(event_id=event.event_id)
        event_repo.acknowledge()


class ProcessPipelineItem(NamedTuple):
    priority: int
    task: Task[Any, FlowExtensionHandlerActionResult]
    kwargs: dict[str, Any]


@app.task(
    autoretry_for=(FlowExtensionRateLimitError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_backoff_max=60 * 60,  # 60 minutes
)
def handle_flow_extension_event(event_id: str) -> None:
    current_logger = logger.bind(event_id=event_id)
    tempdir = tempfile.mkdtemp()
    event = FlowExtensionEventRepository(
        event_id=event_id,
        credential=INVOICE_FLOW_EXTENSION_CREDENTIAL,
    )

    event_data = event.get_data()
    invoice_detail_request = event_data.request["InvoiceDetailRequest"]

    invoice_detail_request_header = invoice_detail_request[
        "InvoiceDetailRequestHeader"
    ]

    invoice_id = invoice_detail_request_header["invoiceID"]

    process_pipeline: list[ProcessPipelineItem] = [
        ProcessPipelineItem(
            priority=100,
            task=verify_ship_to_address,
            kwargs={"event_data": event_data},
        )
    ]

    process_pipeline.sort(key=lambda x: x.priority)
    for process in process_pipeline:
        result: FlowExtensionHandlerActionResult = process.task.delay(
            **process.kwargs
        ).get()
        result = FlowExtensionHandlerActionResult(*result)
        if result.next_action == FlowExtensionHandlerNextAction.HALT:
            message = result.message
            event.halt(message=message)
            current_logger.info(
                "Invoice - %s Halted!",
                invoice_id,
                reason=message,
            )
            return

    event.resume()
    current_logger.info(
        "Invoice - %s Resumed!",
        invoice_id,
    )
    shutil.rmtree(tempdir)

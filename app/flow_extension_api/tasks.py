import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, NamedTuple
from uuid import uuid4

import structlog
from celery import Task

from app.celery import app
from app.flow_extension_api.credential import INVOICE_FLOW_EXTENSION_CREDENTIAL
from app.flow_extension_api.exceptions import FlowExtensionRateLimitError
from app.flow_extension_api.models import (
    FlowExtensionHandlerActionResult,
    FlowExtensionHandlerNextAction,
)
from app.flow_extension_api.repository import (
    FlowExtensionEventRepository,
    get_pending_flow_extension_events,
)
from app.invoice_date_detection.tasks import (
    verify_date_on_cxml_matches_date_on_invoice_pdf,
)
from app.ship_to_detection.tasks import (
    verify_ship_to_address,
)

logger = structlog.get_logger(__name__)


FlowExtensionHandler = Callable[..., FlowExtensionHandlerActionResult]


@app.task(
    autoretry_for=(FlowExtensionRateLimitError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_backoff_max=60 * 60,  # 60 minutes
)
def check_and_handle_invoice_from_flow_extension_api() -> None:
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
    invoice_date_str = invoice_detail_request_header["invoiceDate"]

    invoice_date = datetime.fromisoformat(invoice_date_str).date()
    attachment = event_data.attachment

    process_pipeline: list[ProcessPipelineItem] = [
        ProcessPipelineItem(
            priority=100,
            task=verify_ship_to_address,
            kwargs={"event_data": event_data},
        )
    ]
    if attachment:
        if attachment.content_type == "application/pdf":
            file_path = Path(tempdir) / "invoice.pdf"
            event.save_attachment_to_file(
                cid=attachment.cid,
                file_path=file_path,
            )
            current_logger.info(
                "Invoice attachment saved",
                file_path=str(file_path),
                invoice_id=invoice_id,
            )
            process_pipeline.append(
                ProcessPipelineItem(
                    priority=200,
                    task=verify_date_on_cxml_matches_date_on_invoice_pdf,
                    kwargs={
                        "invoice_id": invoice_id,
                        "invoice_date_on_cxml": invoice_date,
                        "pdf_path": str(file_path),
                    },
                )
            )
        else:
            current_logger.warning(
                "Invoice Date match not supported for " "attachment type: %s",
                attachment.content_type,
            )

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

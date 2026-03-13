from typing import Any
from uuid import uuid4

import structlog

from app.celery import app
from app.flow_extension.exceptions import (
    FlowExtensionRateLimitError,
)
from app.flow_extension.models import (
    FlowExtensionEventData,
    FlowExtensionHandlerActionResult,
    FlowExtensionHandlerNextAction,
)
from app.solutions.ship_to_detection.constants import (
    SHIP_TO_ADDRESS_REFERENCE_DOCUMENT_URL,
)
from app.solutions.ship_to_detection.models import (
    ValidShipToAddress,
)

logger = structlog.get_logger(__name__)


@app.task(
    acks_late=True,  # only remove from queue after successful run
    autoretry_for=(FlowExtensionRateLimitError,),
    retry_backoff=True,
    retry_jitter=True,
)
def verify_ship_to_address(
    *,
    event_data: FlowExtensionEventData,
) -> FlowExtensionHandlerActionResult:
    current_logger = logger.bind(reference=str(uuid4()))
    event_data = FlowExtensionEventData(*event_data)  # type: ignore

    current_logger = current_logger.bind(data=event_data)
    invoice_detail_request = event_data.request["InvoiceDetailRequest"]

    invoice_detail_request_header = invoice_detail_request[
        "InvoiceDetailRequestHeader"
    ]

    invoice_id = invoice_detail_request_header["invoiceID"]
    current_logger = current_logger.bind(invoice_id=invoice_id)

    invoice_detail_shipping = invoice_detail_request_header[
        "InvoiceDetailShipping"
    ]

    shipping_contacts = invoice_detail_shipping["Contact"]

    ship_to_contact = next(
        (
            contact
            for contact in shipping_contacts
            if contact.get("role") == "shipTo"
        ),
        None,
    )

    if not ship_to_contact:
        raise ValueError("Cannot able to find shipTo address", event_data)

    postal_address = ship_to_contact["PostalAddress"]
    name = ship_to_contact["Name"]["content"]

    def halt_event(message: str) -> FlowExtensionHandlerActionResult:
        message = (
            f"{message}, "
            f"Please use this link to find correct address values: "
            f"{SHIP_TO_ADDRESS_REFERENCE_DOCUMENT_URL}"
        )
        return FlowExtensionHandlerActionResult(
            next_action=FlowExtensionHandlerNextAction.HALT,
            message=message,
        )

    try:
        valid_ship_to_address = ValidShipToAddress.objects.get(name=name)
    except ValidShipToAddress.DoesNotExist:
        return halt_event(message=f"Ship to address has invalid name: {name}")

    street_values = postal_address.get("Street", [""] * 3)
    if street_values[1] != "" or street_values[2] != "":
        return halt_event(
            message="Ship to address cannot have any value in Street 2 or 3"
        )

    address_fields: dict[str, Any] = {
        "street": street_values[0],
        "city": postal_address.get("City"),
        "state": postal_address.get("State", {}).get("content"),
        "country": postal_address.get("Country", {}).get("content"),
        "postal_code": postal_address.get("PostalCode"),
    }

    for field, value in address_fields.items():
        if getattr(valid_ship_to_address, field) != value:
            return halt_event(
                message=(
                    f"Ship to address has invalid {field.capitalize()}: "
                    f"{address_fields[field]}"
                )
            )

    return FlowExtensionHandlerActionResult(
        next_action=FlowExtensionHandlerNextAction.CONTINUE
    )

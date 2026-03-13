import json
from pathlib import Path
from typing import Any

import pytest
from django.template import Context, Template

from app.flow_extension.models import (
    FlowExtensionEventData,
    FlowExtensionEventDataAttachment,
    FlowExtensionHandlerNextAction,
)
from app.solutions.ship_to_detection.constants import (
    SHIP_TO_ADDRESS_REFERENCE_DOCUMENT_URL,
)
from app.solutions.ship_to_detection.models import ValidShipToAddress
from app.solutions.ship_to_detection.tasks import (
    verify_ship_to_address,
)


@pytest.fixture(autouse=True)
def create_ship_to_address() -> None:
    ValidShipToAddress.objects.create(
        name="Toronto General Hospital",
        street="200 Elizabeth Street",
        city="Toronto",
        state="ON",
        country="Canada",
        postal_code="M5G 2C4",
    )


def generate_fake_flow_extension_event_data(
    context: dict[str, Any],
) -> FlowExtensionEventData:
    fake_data_file = Path(__file__).parent / "event_data.json"
    json_template = Template(fake_data_file.read_text())
    data_json_text = json_template.render(Context(context))
    response_data = json.loads(data_json_text)

    attachment = None

    if attachment_info := (
        response_data["DataRequest"]["Source"]["AttachmentInfo"]
    ):
        attachment_item = attachment_info["Attachment"]
        attachment = FlowExtensionEventDataAttachment(
            content_type=attachment_item["ContentType"],
            content_length=attachment_item["ContentLength"],
            uri=attachment_item["URI"],
            cid=attachment_item["CID"],
        )

    return FlowExtensionEventData(
        event_id=response_data["DataRequest"]["eventId"],
        request=response_data["DataRequest"]["Source"]["Request"],
        attachment=attachment,
    )


@pytest.mark.django_db
def test_halts_if_invalid_name_found() -> None:
    fake_flow_extension_event_data = generate_fake_flow_extension_event_data(
        context={
            "ship_to_name": "University Health Network",
        }
    )

    sut = verify_ship_to_address.delay(
        event_data=fake_flow_extension_event_data
    ).get()

    assert sut.next_action == FlowExtensionHandlerNextAction.HALT
    assert sut.message == (
        "Ship to address has invalid name: University Health Network, "
        f"Please use this link to find correct address values: {SHIP_TO_ADDRESS_REFERENCE_DOCUMENT_URL}"
    )


@pytest.mark.django_db
def test_halts_if_invalid_street_found() -> None:
    fake_flow_extension_event_data = generate_fake_flow_extension_event_data(
        context={
            "ship_to_name": "Toronto General Hospital",
            "ship_to_street": "404 Elizabeth Street",
        }
    )

    sut = verify_ship_to_address.delay(
        event_data=fake_flow_extension_event_data
    ).get()

    assert sut.next_action == FlowExtensionHandlerNextAction.HALT
    assert sut.message == (
        "Ship to address has invalid Street: 404 Elizabeth Street, "
        f"Please use this link to find correct address values: {SHIP_TO_ADDRESS_REFERENCE_DOCUMENT_URL}"
    )


@pytest.mark.django_db
def test_halts_if_invalid_city_found() -> None:
    fake_flow_extension_event_data = generate_fake_flow_extension_event_data(
        context={
            "ship_to_name": "Toronto General Hospital",
            "ship_to_street": "200 Elizabeth Street",
            "ship_to_city": "New York",
            "ship_to_state": "ON",
            "ship_to_country": "Canada",
            "ship_to_postal_code": "M5G 2C4",
        }
    )

    sut = verify_ship_to_address.delay(
        event_data=fake_flow_extension_event_data
    ).get()

    assert sut.next_action == FlowExtensionHandlerNextAction.HALT
    assert sut.message == (
        "Ship to address has invalid City: New York, "
        f"Please use this link to find correct address values: {SHIP_TO_ADDRESS_REFERENCE_DOCUMENT_URL}"
    )


@pytest.mark.django_db
def test_resumes_if_valid_ship_to_address_found() -> None:
    fake_flow_extension_event_data = generate_fake_flow_extension_event_data(
        context={
            "ship_to_name": "Toronto General Hospital",
            "ship_to_street": "200 Elizabeth Street",
            "ship_to_city": "Toronto",
            "ship_to_state": "ON",
            "ship_to_country": "Canada",
            "ship_to_postal_code": "M5G 2C4",
        }
    )

    sut = verify_ship_to_address.delay(
        event_data=fake_flow_extension_event_data
    ).get()

    assert sut.next_action == FlowExtensionHandlerNextAction.CONTINUE

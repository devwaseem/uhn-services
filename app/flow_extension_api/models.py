from datetime import datetime
from enum import StrEnum
from typing import Any, NamedTuple


class FlowExtensionEvent(NamedTuple):
    event_id: str
    created: datetime
    status: str


class FlowExtensionEventDataAttachment(NamedTuple):
    content_type: str
    content_length: int
    uri: str
    cid: str


class FlowExtensionEventData(NamedTuple):
    event_id: str
    request: dict[str, Any]
    attachment: FlowExtensionEventDataAttachment | None = None


class FlowExtensionHandlerNextAction(StrEnum):
    CONTINUE = "Continue"
    HALT = "Halt"


class FlowExtensionHandlerActionResult(NamedTuple):
    next_action: FlowExtensionHandlerNextAction
    message: str = ""

from datetime import datetime
from json import JSONDecodeError
from pathlib import Path

import httpx

from app.flow_extension.credential import FlowExtensionCredential
from app.flow_extension.exceptions import (
    FlowExtensionAuthFailedError,
    FlowExtensionEventDataNotFoundError,
    FlowExtensionRateLimitError,
)
from app.flow_extension.models import (
    FlowExtensionEvent,
    FlowExtensionEventData,
    FlowExtensionEventDataAttachment,
)


class FlowExtensionEventRepository:
    """Repository for interacting with SAP Ariba Flow Extension Events.

    This repository provides methods to fetch event data and perform actions
    such as acknowledge, halt, resume, or add comments to a specific event
    via the OpenAPI.
    """

    def __init__(
        self,
        event_id: str,
        credential: FlowExtensionCredential,
        runtime_url: str = "https://openapi.ariba.com/api/flowextension/v1/prod/",
    ) -> None:
        """Initialize the repository with an event ID and credentials."""
        self.event_id = event_id
        self.credential = credential
        self.base_url = runtime_url + "flowextensions/"

    def get_data(self) -> FlowExtensionEventData:
        """Fetch the event data and its associated request payload."""
        response = httpx.get(
            url=f"{self.base_url}/{self.credential.flow_extension_id}/events/{self.event_id}/eventdata",
            headers={
                **self._get_default_api_headers(),
                "Accept": "application/json",
            },
        )

        if response.status_code == 404:
            raise FlowExtensionEventDataNotFoundError(response)

        if response.status_code == 401:
            raise FlowExtensionAuthFailedError(response)

        if response.status_code == 429:
            raise FlowExtensionRateLimitError(response=response)

        response.raise_for_status()

        try:
            response_data = response.json()
        except JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON: {response.text}") from exc

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

    def acknowledge(self) -> None:
        """Acknowledge receipt of the flow extension event."""
        response = httpx.post(
            url=f"{self.base_url}/action/{self.credential.flow_extension_id}/events/acknowledge",
            headers={
                **self._get_default_api_headers(),
                "Content-Type": "application/xml",
            },
            content=f"<events><event><eventId>{self.event_id}</eventId></event></events>",
        )

        if response.status_code == 404:
            raise FlowExtensionEventDataNotFoundError(response)

        if response.status_code == 401:
            raise FlowExtensionAuthFailedError(response)

        if response.status_code == 429:
            raise FlowExtensionRateLimitError(response=response)

        response.raise_for_status()

    def halt(self, message: str) -> None:
        """Halt the event processing in Ariba with a specific message."""
        response = httpx.post(
            url=f"{self.base_url}/action/{self.credential.flow_extension_id}/events/{self.event_id}/halt",
            content=message,
            headers=self._get_default_api_headers(),
        )

        if response.status_code == 404:
            raise FlowExtensionEventDataNotFoundError(response)

        if response.status_code == 401:
            raise FlowExtensionAuthFailedError(response)

        if response.status_code == 429:
            raise FlowExtensionRateLimitError(response=response)

        response.raise_for_status()

    def resume(self) -> None:
        """Resume the event processing in Ariba."""
        response = httpx.post(
            url=f"{self.base_url}/action/{self.credential.flow_extension_id}/events/{self.event_id}/resume",
            headers=self._get_default_api_headers(),
        )

        if response.status_code == 404:
            raise FlowExtensionEventDataNotFoundError(response)

        if response.status_code == 401:
            raise FlowExtensionAuthFailedError(response)

        if response.status_code == 429:
            raise FlowExtensionRateLimitError(response=response)

        response.raise_for_status()

    def add_comment(self, comment: str) -> None:
        """Add a comment to the flow extension event."""
        response = httpx.post(
            url=f"{self.base_url}/{self.credential.flow_extension_id}/events/{self.event_id}",
            data={"comment": comment},
            headers=self._get_default_api_headers(),
        )

        if response.status_code == 404:
            raise FlowExtensionEventDataNotFoundError(response)

        if response.status_code == 401:
            raise FlowExtensionAuthFailedError(response)

        if response.status_code == 429:
            raise FlowExtensionRateLimitError(response=response)

        response.raise_for_status()

    def save_attachment_to_file(self, cid: str, file_path: Path) -> None:
        """Download and save the attachment to the local file system."""
        response = httpx.get(
            url=f"{self.base_url}/{self.credential.flow_extension_id}/events/{self.event_id}/eventdata/attachment?cid={cid}",
            headers=self._get_default_api_headers(),
        )

        if response.status_code == 404:
            raise FlowExtensionEventDataNotFoundError(response)

        if response.status_code == 401:
            raise FlowExtensionAuthFailedError(response)

        if response.status_code == 429:
            raise FlowExtensionRateLimitError(response=response)

        response.raise_for_status()

        file_path.write_bytes(response.content)

    def _get_default_api_headers(self) -> dict[str, str]:
        """Generate the default headers required for API authentication."""
        return {
            "Authorization": f"Basic {self.credential.http_basic_token}",
            "apiKey": self.credential.api_key,
        }


def get_pending_flow_extension_events(
    credential: FlowExtensionCredential,
    runtime_url: str = "https://openapi.ariba.com/api/flowextension/v1/prod/",
    max_count: int = -1,
) -> list[FlowExtensionEvent]:
    """Retrieve a list of pending flow extension events."""
    url = f"{runtime_url}flowextensions/{credential.flow_extension_id}/events"
    if max_count > 0:
        url += f"?count={max_count}"

    response = httpx.get(
        url,
        headers={
            "Authorization": f"Basic {credential.http_basic_token}",
            "apiKey": credential.api_key,
        },
    )

    if response.status_code == 204:
        return []

    if response.status_code == 401:
        raise FlowExtensionAuthFailedError(response)

    if response.status_code == 429:
        raise FlowExtensionRateLimitError(response=response)

    response.raise_for_status()

    response_data = response.json()

    return [
        FlowExtensionEvent(
            event_id=item["eventId"],
            created=datetime.fromisoformat(item["created"]),
            status=item["status"],
        )
        for item in response_data["events"]
    ]

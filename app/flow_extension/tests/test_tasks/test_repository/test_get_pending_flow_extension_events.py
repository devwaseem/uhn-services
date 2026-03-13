from unittest.mock import MagicMock, patch

import pytest

from app.flow_extension.credential import FlowExtensionCredential
from app.flow_extension.exceptions import (
    FlowExtensionAuthFailedError,
    FlowExtensionRateLimitError,
)
from app.flow_extension.repository import (
    get_pending_flow_extension_events,
)


def test_returns_events_correctly_if_found_for_status_code_200() -> None:
    with patch(
        "app.flow_extension.repository.httpx.get"
    ) as mock_httpx_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "flowExtensionId": "UHN_Invoice_FE",
            "events": [
                {
                    "eventId": "PrM5IrdDQOGj4zcHxi5gRQ",
                    "created": "2024-08-12T05:42:24-0700",
                    "status": "PREPARED",
                    "numEventId": 1.10000000000000000000463642e26,
                }
            ],
        }

        mock_httpx_get.return_value = mock_response

        events = get_pending_flow_extension_events(
            FlowExtensionCredential(
                flow_extension_id="flow_extension_id",
                http_basic_token="http_basic_token",
                api_key="api_key",
            )
        )
        mock_httpx_get.assert_called()

        assert len(events) == 1

        assert events[0].event_id == "PrM5IrdDQOGj4zcHxi5gRQ"
        assert events[0].status == "PREPARED"


def test_returns_empty_events_for_status_code_204() -> None:
    with patch(
        "app.flow_extension.repository.httpx.get"
    ) as mock_httpx_get:
        mock_response = MagicMock()
        mock_response.status_code = 204

        mock_httpx_get.return_value = mock_response

        events = get_pending_flow_extension_events(
            FlowExtensionCredential(
                flow_extension_id="flow_extension_id",
                http_basic_token="http_basic_token",
                api_key="api_key",
            )
        )

        assert len(events) == 0


def test_throws_auth_failed_error_for_status_code_401() -> None:
    with patch(
        "app.flow_extension.repository.httpx.get"
    ) as mock_httpx_get:
        mock_response = MagicMock()
        mock_response.status_code = 401

        mock_httpx_get.return_value = mock_response

        with pytest.raises(FlowExtensionAuthFailedError):
            get_pending_flow_extension_events(
                FlowExtensionCredential(
                    flow_extension_id="flow_extension_id",
                    http_basic_token="http_basic_token",
                    api_key="api_key",
                )
            )


def test_throws_rate_limit_error_for_status_code_429() -> None:
    with patch(
        "app.flow_extension.repository.httpx.get"
    ) as mock_httpx_get:
        mock_response = MagicMock()
        mock_response.status_code = 429

        mock_httpx_get.return_value = mock_response

        with pytest.raises(FlowExtensionRateLimitError):
            get_pending_flow_extension_events(
                FlowExtensionCredential(
                    flow_extension_id="flow_extension_id",
                    http_basic_token="http_basic_token",
                    api_key="api_key",
                )
            )

"""Tests for network helper utilities."""

from __future__ import annotations

from typing import Any

from django.test import RequestFactory

from app.helpers.network import get_ip_from_request


def test_get_ip_from_request_returns_routable_ip(
    monkeypatch: Any,
) -> None:
    """Network helper returns IP when routable."""
    monkeypatch.setattr(
        "app.helpers.network.get_client_ip",
        lambda request: ("203.0.113.10", True),
    )
    request = RequestFactory().get("/")

    assert get_ip_from_request(request) == "203.0.113.10"


def test_get_ip_from_request_returns_none_when_unroutable(
    monkeypatch: Any,
) -> None:
    """Network helper returns None for unroutable IPs."""
    monkeypatch.setattr(
        "app.helpers.network.get_client_ip",
        lambda request: ("203.0.113.10", False),
    )
    request = RequestFactory().get("/")

    assert get_ip_from_request(request) is None


def test_get_ip_from_request_returns_none_when_missing(
    monkeypatch: Any,
) -> None:
    """Network helper returns None when IP is missing."""
    monkeypatch.setattr(
        "app.helpers.network.get_client_ip",
        lambda request: (None, True),
    )
    request = RequestFactory().get("/")

    assert get_ip_from_request(request) is None

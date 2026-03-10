"""Tests for template tag helpers."""

from __future__ import annotations

import re

from app.templatetags.bold_for import bold_for
from app.templatetags.replace import replace
from app.templatetags.trim import trim
from app.templatetags.uuid4 import uuid4


def test_bold_for_wraps_match() -> None:
    """bold_for wraps the matching substring."""
    result = bold_for("Rezolution Engine", "Engine")

    assert "<strong>Engine</strong>" in result


def test_replace_returns_value_when_invalid_arg() -> None:
    """replace ignores invalid arguments."""
    assert replace("aaa", "invalid") == "aaa"


def test_replace_swaps_value() -> None:
    """replace swaps values when valid argument provided."""
    assert replace("aaa", "a|b") == "bbb"


def test_trim_removes_whitespace() -> None:
    """trim strips whitespace."""
    assert trim("  value ") == "value"


def test_uuid4_replaces_placeholder() -> None:
    """uuid4 replaces placeholder tokens with UUIDs."""
    result = uuid4("uuid4")

    assert "uuid4" not in result
    assert re.match(r"^[0-9a-f\-]{36}$", result)

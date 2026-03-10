"""Tests for string helper utilities."""

from __future__ import annotations

from app.helpers.string import mark_as_strong_for, unique_split


def test_unique_split_returns_unique_values() -> None:
    """unique_split trims and de-duplicates entries."""
    result = unique_split("alpha, beta, alpha,", delimiter=",")

    assert set(result) == {"alpha", "beta"}


def test_mark_as_strong_for_wraps_match() -> None:
    """mark_as_strong_for wraps the matched substring."""
    result = mark_as_strong_for("Rezolution Engine", "engine")

    assert "<strong>Engine</strong>" in result


def test_mark_as_strong_for_returns_original_when_missing() -> None:
    """mark_as_strong_for returns original string when missing."""
    value = "Rezolution"

    assert mark_as_strong_for(value, "missing") == value

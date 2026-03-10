"""Tests for object helper utilities."""

from __future__ import annotations

from dataclasses import dataclass

from app.helpers.object import has_any_field_valid, object_or_none, value_or_none


@dataclass
class _Sample:
    """Sample data structure for field checks."""

    name: str
    count: int


def test_has_any_field_valid_detects_value() -> None:
    """Field validation returns True when any field is populated."""
    sample = _Sample(name="", count=2)

    assert has_any_field_valid(sample, fields=["name", "count"]) is True


def test_has_any_field_valid_returns_false_when_empty() -> None:
    """Field validation returns False when all fields are empty."""
    sample = _Sample(name="", count=0)

    assert has_any_field_valid(sample, fields=["name"]) is False


def test_object_or_none_returns_value_for_true_condition() -> None:
    """object_or_none returns the value when condition is truthy."""
    assert object_or_none(condition=True, return_value="value") == "value"


def test_object_or_none_returns_none_for_false_condition() -> None:
    """object_or_none returns None when condition is False."""
    assert object_or_none(condition=False, return_value="value") is None


def test_object_or_none_accepts_non_boolean_condition() -> None:
    """object_or_none handles non-boolean truthy values."""
    assert object_or_none(condition="present", return_value=123) == 123


def test_object_or_none_handles_falsy_non_boolean() -> None:
    """object_or_none returns None for falsy non-boolean values."""
    assert object_or_none(condition=0, return_value="value") is None


def test_value_or_none_returns_value() -> None:
    """value_or_none returns the provided non-null value."""
    assert value_or_none("value") == "value"


def test_value_or_none_returns_none() -> None:
    """value_or_none returns None when passed None."""
    assert value_or_none(None) is None

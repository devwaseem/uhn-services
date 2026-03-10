"""Tests for file validators."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from django.core.exceptions import ValidationError

from app.validators.file_validators import FileSizeValidatorInMb


def test_file_size_validator_allows_small_file() -> None:
    """Validator does nothing for files under the limit."""
    validator = FileSizeValidatorInMb(1)
    file_obj = SimpleNamespace(size=200 * 1024)

    validator(file_obj)


def test_file_size_validator_rejects_large_file() -> None:
    """Validator raises for files exceeding limit."""
    validator = FileSizeValidatorInMb(1)
    file_obj = SimpleNamespace(size=2 * 1024 * 1024)

    with pytest.raises(ValidationError) as excinfo:
        validator(file_obj)

    assert "exceeding" in str(excinfo.value)


def test_file_size_validator_equality() -> None:
    """Validator equality compares configuration."""
    assert FileSizeValidatorInMb(1) == FileSizeValidatorInMb(1)
    assert FileSizeValidatorInMb(1) != FileSizeValidatorInMb(2)
    assert FileSizeValidatorInMb(1) != object()


def test_file_size_validator_custom_message_and_code() -> None:
    """Validator uses custom message and code overrides."""
    validator = FileSizeValidatorInMb(
        1, message="Custom error", code="custom_code"
    )
    file_obj = SimpleNamespace(size=2 * 1024 * 1024)

    with pytest.raises(ValidationError) as excinfo:
        validator(file_obj)

    assert "Custom error" in str(excinfo.value)
    assert excinfo.value.error_list[0].code == "custom_code"

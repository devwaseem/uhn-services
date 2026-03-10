"""Tests for core models."""

from __future__ import annotations

import pytest
from django.utils.translation import gettext as _

from app.account.models import User
from app.models.base import TimeStampedModel, TimestampedUUIDModel


@pytest.mark.django_db
def test_user_manager_create_superuser_validates_flags() -> None:
    """Superuser creation enforces staff and superuser flags."""
    with pytest.raises(ValueError, match="is_staff=True"):
        User.objects.create_superuser(
            email="badstaff@example.com",
            password="pass",
            is_staff=False,
        )

    with pytest.raises(ValueError, match="is_superuser=True"):
        User.objects.create_superuser(
            email="badroot@example.com",
            password="pass",
            is_superuser=False,
        )

    user = User.objects.create_superuser(
        email="root@example.com", password="pass"
    )
    assert user.is_staff is True
    assert user.is_superuser is True


def test_base_models_are_abstract() -> None:
    """Base model classes remain abstract."""
    assert TimeStampedModel._meta.abstract is True  # noqa: SLF001
    assert TimestampedUUIDModel._meta.abstract is True  # noqa: SLF001
    assert _(TimeStampedModel.__name__) is not None

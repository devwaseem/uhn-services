"""Tests for update_model_field_if_empty helper."""

from __future__ import annotations

import pytest
from mixer.backend.django import mixer

from app.account.models import User
from app.helpers.django_models import update_model_field_if_empty


@pytest.mark.django_db
def test_update_model_field_if_empty_raises_for_missing_attr() -> None:
    """update_model_field_if_empty raises when attribute is missing."""
    user = mixer.blend(User, name="Jane")

    with pytest.raises(KeyError, match="missing not found"):
        update_model_field_if_empty(
            instance=user,
            attr="missing",
            value="value",
        )


@pytest.mark.django_db
def test_update_model_field_if_empty_updates_empty_value() -> None:
    """update_model_field_if_empty updates when field is empty."""
    user = mixer.blend(User, name="")

    update_model_field_if_empty(instance=user, attr="name", value="New")

    assert user.name == "New"


@pytest.mark.django_db
def test_update_model_field_if_empty_leaves_existing_value() -> None:
    """update_model_field_if_empty keeps existing values."""
    user = mixer.blend(User, name="Existing")

    update_model_field_if_empty(instance=user, attr="name", value="New")

    assert user.name == "Existing"

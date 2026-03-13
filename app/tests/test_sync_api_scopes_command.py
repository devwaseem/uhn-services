from __future__ import annotations

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from app.api_auth.models import APIScopes
from app.api_auth.scope_registry import AllowedScopes, get_scope_definitions


@pytest.mark.django_db
def test_sync_api_scopes_check_fails_when_db_has_drift() -> None:
    with pytest.raises(CommandError, match="API scope drift detected"):
        call_command("sync_api_scopes", "--check")


@pytest.mark.django_db
def test_sync_api_scopes_apply_creates_registry_scopes() -> None:
    call_command("sync_api_scopes", "--apply")

    expected_slugs = {
        definition.slug.value for definition in get_scope_definitions()
    }
    actual_slugs = set(APIScopes.objects.values_list("slug", flat=True))
    assert actual_slugs == expected_slugs
    assert APIScopes.objects.filter(is_active=True).count() == len(
        expected_slugs
    )


@pytest.mark.django_db
def test_sync_api_scopes_apply_updates_and_deprecates() -> None:
    APIScopes.objects.create(
        slug=AllowedScopes.NON_PO_INVOICES_READ,
        description="old",
        is_active=False,
    )
    legacy_scope = APIScopes.objects.create(
        slug="legacy.scope",
        description="legacy",
        is_active=True,
    )

    call_command("sync_api_scopes", "--apply")

    expected_description = next(
        definition.description
        for definition in get_scope_definitions()
        if definition.slug is AllowedScopes.NON_PO_INVOICES_READ
    )
    refreshed_scope = APIScopes.objects.get(
        slug=AllowedScopes.NON_PO_INVOICES_READ
    )
    assert refreshed_scope.is_active is True
    assert refreshed_scope.description == expected_description

    legacy_scope.refresh_from_db()
    assert legacy_scope.is_active is False


@pytest.mark.django_db
def test_sync_api_scopes_check_passes_after_apply() -> None:
    call_command("sync_api_scopes", "--apply")

    call_command("sync_api_scopes", "--check")

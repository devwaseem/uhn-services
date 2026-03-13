from datetime import timedelta

import pytest
from django.test import RequestFactory
from django.utils import timezone
from ninja.errors import HttpError

from app.api_auth.models import APIKey, APIScopes
from app.api_auth.permissions import ScopedAuth
from app.api_auth.scope_registry import AllowedScopes


@pytest.mark.django_db
def test_scope_auth_allows_valid_key_and_scope() -> None:
    solution = APIScopes.objects.create(
        slug=AllowedScopes.NON_PO_INVOICES_READ,
    )
    api_key = APIKey.objects.create(name="Invoices key")
    raw_key = api_key.generate_key(commit=True)
    api_key.allowed_solutions.add(solution)

    request = RequestFactory().get(
        "/api/non-po-invoices/non-po-invoices/",
        HTTP_AUTHORIZATION=f"Bearer {raw_key}",
        REMOTE_ADDR="203.0.113.10",
    )

    auth = ScopedAuth(scope_code=AllowedScopes.NON_PO_INVOICES_READ)
    authenticated_key = auth.authenticate(request=request, token=raw_key)

    assert authenticated_key is not None
    assert authenticated_key.id == api_key.id

    api_key.refresh_from_db()
    assert api_key.last_used_at is not None


@pytest.mark.django_db
def test_scope_auth_accepts_bearer_authorization_header() -> None:
    scope = APIScopes.objects.create(
        slug=AllowedScopes.CONTRACT_WORKSPACES_READ,
    )
    api_key = APIKey.objects.create(name="Bearer auth key")
    raw_key = api_key.generate_key(commit=True)
    api_key.allowed_solutions.add(scope)

    request = RequestFactory().get(
        "/api/contract-workspaces/",
        HTTP_AUTHORIZATION=f"Bearer {raw_key}",
    )
    auth = ScopedAuth(scope_code=AllowedScopes.CONTRACT_WORKSPACES_READ)

    authenticated_key = auth(request)

    assert authenticated_key is not None
    assert authenticated_key.id == api_key.id


@pytest.mark.django_db
def test_scope_auth_rejects_missing_scope() -> None:
    APIScopes.objects.create(slug=AllowedScopes.NON_PO_INVOICES_READ)
    api_key = APIKey.objects.create(name="Workspaces key")
    raw_key = api_key.generate_key(commit=True)

    request = RequestFactory().get(
        "/api/non-po-invoices/non-po-invoices/",
        HTTP_AUTHORIZATION=f"Bearer {raw_key}",
    )

    auth = ScopedAuth(scope_code=AllowedScopes.NON_PO_INVOICES_READ)

    with pytest.raises(HttpError) as error:
        auth.authenticate(request=request, token=raw_key)

    assert error.value.status_code == 403


@pytest.mark.django_db
def test_scope_auth_rejects_inactive_scope() -> None:
    inactive_scope = APIScopes.objects.create(
        slug=AllowedScopes.NON_PO_INVOICES_READ,
        is_active=False,
    )
    api_key = APIKey.objects.create(name="Invoices key inactive scope")
    raw_key = api_key.generate_key(commit=True)
    api_key.allowed_solutions.add(inactive_scope)

    request = RequestFactory().get(
        "/api/non-po-invoices/non-po-invoices/",
        HTTP_AUTHORIZATION=f"Bearer {raw_key}",
    )
    auth = ScopedAuth(scope_code=AllowedScopes.NON_PO_INVOICES_READ)

    with pytest.raises(HttpError) as error:
        auth.authenticate(request=request, token=raw_key)

    assert error.value.status_code == 403


@pytest.mark.django_db
def test_scope_auth_rejects_inactive_or_expired_or_revoked_key() -> None:
    solution = APIScopes.objects.create(
        slug=AllowedScopes.CONTRACT_WORKSPACES_READ,
    )
    api_key = APIKey.objects.create(name="Contract key")
    raw_key = api_key.generate_key(commit=True)
    api_key.allowed_solutions.add(solution)

    request = RequestFactory().get(
        "/api/contract-workspaces/",
        HTTP_AUTHORIZATION=f"Bearer {raw_key}",
    )
    auth = ScopedAuth(scope_code=AllowedScopes.CONTRACT_WORKSPACES_READ)

    api_key.is_active = False
    api_key.save(update_fields=["is_active"])
    assert auth.authenticate(request=request, token=raw_key) is None

    api_key.is_active = True
    api_key.expires_at = timezone.now() - timedelta(minutes=1)
    api_key.save(update_fields=["is_active", "expires_at"])
    assert auth.authenticate(request=request, token=raw_key) is None

    api_key.expires_at = None
    api_key.revoked_at = timezone.now()
    api_key.save(update_fields=["expires_at", "revoked_at"])
    assert auth.authenticate(request=request, token=raw_key) is None


@pytest.mark.django_db
def test_api_key_is_encrypted_at_rest() -> None:
    api_key = APIKey.objects.create(name="Encryption key")
    raw_key = api_key.generate_key(commit=True)
    api_key.refresh_from_db()

    assert api_key.key != raw_key
    assert api_key.get_raw_key() == raw_key
    assert api_key.verify_key(raw_key)

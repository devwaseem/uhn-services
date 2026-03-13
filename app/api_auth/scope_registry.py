"""Code-first registry for API scopes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AllowedScopes(StrEnum):
    """Scope slugs referenced by endpoint auth declarations."""

    NON_PO_INVOICES_READ = "non_po_invoices.read"
    CONTRACT_WORKSPACES_READ = "contract_workspaces.read"


@dataclass(frozen=True, slots=True)
class ScopeDefinition:
    """Registry metadata for one API scope."""

    slug: AllowedScopes
    description: str


_SCOPE_DEFINITIONS: tuple[ScopeDefinition, ...] = (
    ScopeDefinition(
        slug=AllowedScopes.NON_PO_INVOICES_READ,
        description="Read non-PO invoice records.",
    ),
    ScopeDefinition(
        slug=AllowedScopes.CONTRACT_WORKSPACES_READ,
        description="Read contract workspace records.",
    ),
)


def get_scope_definitions() -> tuple[ScopeDefinition, ...]:
    """Return all code-defined scopes used by the API."""

    return _SCOPE_DEFINITIONS


def get_scope_slugs() -> set[str]:
    """Return normalized scope slug strings from the registry."""

    return {definition.slug.value for definition in _SCOPE_DEFINITIONS}

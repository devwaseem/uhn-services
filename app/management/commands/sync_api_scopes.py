"""Synchronize API scopes from the code registry to the database."""

from __future__ import annotations

from dataclasses import dataclass

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from app.api_auth.models import APIScopes
from app.api_auth.scope_registry import ScopeDefinition, get_scope_definitions


@dataclass(slots=True)
class ScopeSyncResult:
    """Stores scope synchronization counts."""

    created: int = 0
    updated: int = 0
    activated: int = 0
    deprecated: int = 0

    @property
    def has_drift(self) -> bool:
        return (
            self.created > 0
            or self.updated > 0
            or self.activated > 0
            or self.deprecated > 0
        )


def _collect_sync_result(
    *,
    existing_by_slug: dict[str, APIScopes],
    desired_by_slug: dict[str, ScopeDefinition],
) -> ScopeSyncResult:
    result = ScopeSyncResult()

    for slug, scope in desired_by_slug.items():
        existing_scope = existing_by_slug.get(slug)
        if existing_scope is None:
            result.created += 1
            continue

        if existing_scope.description != scope.description:
            result.updated += 1

        if not existing_scope.is_active:
            result.activated += 1

    for slug, existing_scope in existing_by_slug.items():
        if slug not in desired_by_slug and existing_scope.is_active:
            result.deprecated += 1

    return result


def _apply_sync(
    *,
    existing_by_slug: dict[str, APIScopes],
    desired_by_slug: dict[str, ScopeDefinition],
) -> ScopeSyncResult:
    result = ScopeSyncResult()

    with transaction.atomic():
        for slug, scope in desired_by_slug.items():
            existing_scope = existing_by_slug.get(slug)
            if existing_scope is None:
                APIScopes.objects.create(
                    slug=slug,
                    description=scope.description,
                    is_active=True,
                )
                result.created += 1
                continue

            update_fields: list[str] = []
            if existing_scope.description != scope.description:
                existing_scope.description = scope.description
                update_fields.append("description")
                result.updated += 1

            if not existing_scope.is_active:
                existing_scope.is_active = True
                update_fields.append("is_active")
                result.activated += 1

            if update_fields:
                existing_scope.save(update_fields=update_fields)

        for slug, existing_scope in existing_by_slug.items():
            if slug in desired_by_slug or not existing_scope.is_active:
                continue
            existing_scope.is_active = False
            existing_scope.save(update_fields=["is_active"])
            result.deprecated += 1

    return result


class Command(BaseCommand):
    """Sync code-defined API scopes into APIScopes."""

    help = "Synchronize API scopes from code registry into database"

    def add_arguments(self, parser) -> None:  # noqa: ANN001
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply sync changes to the database",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Check for drift and fail if changes are required",
        )

    def handle(self, *args: object, **options: object) -> str:
        _ = args
        apply_mode = bool(options.get("apply"))
        check_mode = bool(options.get("check"))

        if apply_mode and check_mode:
            raise CommandError("Use either --apply or --check, not both")

        if not apply_mode and not check_mode:
            check_mode = True

        desired_by_slug = {
            definition.slug.value: definition
            for definition in get_scope_definitions()
        }
        existing_by_slug = {
            scope.slug: scope for scope in APIScopes.objects.all()
        }

        if check_mode:
            result = _collect_sync_result(
                existing_by_slug=existing_by_slug,
                desired_by_slug=desired_by_slug,
            )
            if result.has_drift:
                message = (
                    "API scope drift detected: "
                    f"create={result.created}, "
                    f"update={result.updated}, "
                    f"activate={result.activated}, "
                    f"deprecate={result.deprecated}. "
                    "Run `python manage.py sync_api_scopes --apply`."
                )
                raise CommandError(message)

            self.stdout.write(
                self.style.SUCCESS("No API scope drift detected")
            )
            return ""

        result = _apply_sync(
            existing_by_slug=existing_by_slug,
            desired_by_slug=desired_by_slug,
        )
        self.stdout.write(
            self.style.SUCCESS(
                "API scope sync completed: "
                f"create={result.created}, "
                f"update={result.updated}, "
                f"activate={result.activated}, "
                f"deprecate={result.deprecated}"
            )
        )
        return ""

from enum import StrEnum
from typing import Any, NamedTuple

from django.http import HttpRequest
from ninja.errors import HttpError
from ninja.security import APIKeyHeader

from app.api_auth.models import APIKey


class Solution(NamedTuple):
    id: str
    name: str


class AllowedSolutions(StrEnum):
    NON_PO_INVOICES = "non-po-invoices"
    CONTRACT_WORKSPACES = "contract-workspaces"


class SolutionAuth(APIKeyHeader):
    param_name = "X-API-Key"

    def __init__(self, solution_name: AllowedSolutions) -> None:
        self.solution_name = solution_name
        super().__init__()

    def authenticate(
        self,
        request: HttpRequest,  # noqa
        key: str | None,
    ) -> Any | None:
        if not key:
            return None

        try:
            api_key = APIKey.objects.prefetch_related("allowed_solutions").get(
                key=key, is_active=True
            )
        except APIKey.DoesNotExist:
            return None

        allowed = api_key.allowed_solutions.filter(
            name=self.solution_name
        ).exists()
        if not allowed:
            raise HttpError(
                status_code=403,
                message="You do not have permission to access this resource",
            )

        return True

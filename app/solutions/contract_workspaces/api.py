import httpx
from django.http import HttpRequest, JsonResponse
from ninja import Router

from app.api_auth.permissions import (
    AllowedScopes,
    ScopedAuth,
)
from app.ariba import contract_workspace
from app.ariba.auth import AribaOAuthManager
from env import Env

router = Router()

_ARIBA_OAUTH = AribaOAuthManager(
    username=Env.str("OPERATIONAL_REPORTING_FOR_SOURCING_API_USERNAME"),  # type: ignore
    password=Env.str("OPERATIONAL_REPORTING_FOR_SOURCING_API_PASSWORD"),  # type: ignore
)
_API_KEY: str = Env.str("OPERATIONAL_REPORTING_FOR_SOURCING_API_KEY")  # type: ignore
_REALM: str = Env.str("OPERATIONAL_REPORTING_FOR_SOURCING_API_REALM")  # type: ignore


@router.get(
    "/",
    auth=ScopedAuth(scope_code=AllowedScopes.CONTRACT_WORKSPACES_READ),
)
async def contract_workspaces(
    request: HttpRequest,  # noqa
    page_token: str | None = None,
) -> JsonResponse:
    async with httpx.AsyncClient() as client:
        token = await _ARIBA_OAUTH.get_token(client=client)
        try:
            results = await contract_workspace.get_view(
                client=client,
                auth_token=token,
                api_key=_API_KEY,
                name="ContractWorkspaceAll",
                realm=_REALM,
                page_token=page_token,
            )
            return JsonResponse(results)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 409:
                return JsonResponse(
                    {"message": "Too many requests"},
                    status=429,
                )
            raise exc from exc

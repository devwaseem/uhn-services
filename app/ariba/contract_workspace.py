from typing import Any

import httpx

from app.ariba.auth import AribaOAuthToken

_BASE_URL = "https://openapi.ariba.com/api/sourcing-reporting-details/v1/prod"


class ContractWorkspaceAuthenticationError(Exception): ...


async def get_view(
    *,
    client: httpx.AsyncClient,
    auth_token: AribaOAuthToken,
    api_key: str,
    name: str,
    realm: str,
    page_token: str | None = None,
) -> dict[str, Any]:
    url = f"{_BASE_URL}/views/{name}"
    params = {
        "realm": realm,
    }
    if page_token:
        params["PageToken"] = page_token
    response = await client.get(
        url=url,
        params=params,
        timeout=300,  # 5 minutes
        headers={
            "Authorization": f"Bearer {auth_token.access_token}",
            "apiKey": api_key,
        },
    )
    if response.status_code == 401:
        raise ContractWorkspaceAuthenticationError(response=response)

    response.raise_for_status()
    return response.json()

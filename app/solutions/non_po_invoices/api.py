from datetime import date, datetime, time, timezone
from typing import Any

import httpx
from django.http import HttpRequest, JsonResponse
from ninja import Query, Router

from app.api_auth.permissions import (
    AllowedSolutions,
    SolutionAuth,
)
from app.ariba import operational_procurement
from app.ariba.auth import AribaOAuthManager
from env import Env

router = Router()

_ARIBA_OAUTH = AribaOAuthManager(
    username=Env.str("OPERATIONAL_PROCUREMENT_API_USERNAME"),  # type: ignore
    password=Env.str("OPERATIONAL_PROCUREMENT_API_PASSWORD"),  # type: ignore
)
_API_KEY: str = Env.str("OPERATIONAL_PROCUREMENT_API_KEY")  # type: ignore
_REALM: str = Env.str("OPERATIONAL_PROCUREMENT_API_REALM")  # type: ignore


_EXAMPLE_DATE = datetime.now(tz=timezone.utc).date()


@router.get(
    path="/non-po-invoices/",
    auth=SolutionAuth(solution_name=AllowedSolutions.NON_PO_INVOICES),
)
async def non_po_invoices(
    request: HttpRequest,  # noqa
    date_from: date = Query(example=_EXAMPLE_DATE),  # noqa  # type: ignore
    date_to: date = Query(example=_EXAMPLE_DATE),  # noqa  # type: ignore
    page_token: str | None = None,
) -> JsonResponse:
    async with httpx.AsyncClient() as client:
        token = await _ARIBA_OAUTH.get_token(client=client)
        filters = {
            "createdDateFrom": datetime.combine(
                date=date_from, time=time(0, 0)
            )
            .astimezone(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z"),
            "createdDateTo": datetime.combine(date=date_to, time=time(0, 0))
            .astimezone(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z"),
        }
        try:
            results = await operational_procurement.get_view(
                client=client,
                auth_token=token,
                api_key=_API_KEY,
                name="Invoice_UHN_createdRange",
                realm=_REALM,
                filters=filters,
                page_token=page_token,
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 409:
                return JsonResponse(
                    {"message": "Too many requests"},
                    status=429,
                )
            raise exc from exc
        records: list[dict[str, Any]] = results["Records"]
        po_only_invoice_records = [
            record for record in records if record["IsNonPO"] is True
        ]
        results["Records"] = po_only_invoice_records
        return JsonResponse(results)

from typing import Any

from django.http import HttpRequest
from django.utils import timezone
from ninja.errors import HttpError
from ninja.security import HttpBearer

from app.api_auth.models import APIKey
from app.api_auth.scope_registry import AllowedScopes


def require_scope(*, api_key: APIKey, scope_code: AllowedScopes) -> None:
    is_allowed = api_key.allowed_solutions.filter(
        slug=scope_code,
        is_active=True,
    ).exists()
    if not is_allowed:
        raise HttpError(
            status_code=403,
            message="You do not have permission to access this resource",
        )


class APIKeyAuth(HttpBearer):
    def authenticate(
        self,
        request: HttpRequest,  # noqa
        token: str,
    ) -> APIKey | None:
        key = token.strip()
        if not key:
            return None

        key_prefix = APIKey.get_key_prefix(key)
        key_hash = APIKey.get_key_hash(key)
        try:
            api_key = APIKey.objects.get(
                key_prefix=key_prefix,
                key_hash=key_hash,
            )
        except APIKey.DoesNotExist:
            return None

        if not api_key.can_authenticate(at=timezone.now()):
            return None

        return api_key


class ScopedAuth(APIKeyAuth):
    def __init__(self, *, scope_code: AllowedScopes) -> None:
        self.scope_code = scope_code
        super().__init__()

    def authenticate(
        self,
        request: HttpRequest,
        token: str,
    ) -> Any | None:
        api_key = super().authenticate(request=request, token=token)
        if api_key is None:
            return None

        require_scope(api_key=api_key, scope_code=self.scope_code)
        api_key.mark_used(request=request)

        return api_key

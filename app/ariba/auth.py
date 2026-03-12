import base64
import hashlib
from datetime import datetime, timedelta
from typing import NamedTuple, Self

import httpx
from django.core.cache import cache
from django.utils import timezone
from httpx import AsyncClient

_CACHE_VERSION = 1


class AribaAuthWrongCredentialError(Exception):
    def __init__(self, response: httpx.Response) -> None:
        self.response = response


class AribaOAuthToken(NamedTuple):
    date_created: datetime
    access_token: str
    refresh_token: str
    expires_in: int

    def is_expired(self) -> bool:
        return bool(
            self.date_created + timedelta(seconds=self.expires_in)
            < timezone.now()
        )


class AribaOAuthManager:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.base64_encoded_secret_key = base64.b64encode(
            f"{username}:{password}".encode("utf-8")
        ).decode("utf-8")
        self.cache_key = (
            f"ARIBAAUTH:{_CACHE_VERSION}:"
            + hashlib.md5(
                self.base64_encoded_secret_key.encode("utf-8"),
                usedforsecurity=True,
            ).hexdigest()
        )

    async def get_token(
        self: Self, client: AsyncClient | None = None
    ) -> AribaOAuthToken:
        if cached_data := cache.get(key=self.cache_key):
            token = AribaOAuthToken(*cached_data)
            if not token.is_expired():
                return token
            new_token = await self.login(
                client=client,
                refresh_token=token.refresh_token,
            )
            cache.set(key=self.cache_key, value=new_token)
            return new_token
        new_token = await self.login(
            client=client,
        )
        cache.set(key=self.cache_key, value=new_token)
        return new_token

    async def login(
        self: Self,
        *,
        client: AsyncClient | None = None,
        refresh_token: str | None = None,
    ) -> AribaOAuthToken:
        _should_close_client = False
        if not client:
            client = httpx.AsyncClient()
            _should_close_client = True

        data = {
            "grant_type": "client_credentials",
        }
        if refresh_token:
            data["grant_type"] = "refresh_token"
            data["refresh_token"] = refresh_token

        response = await client.post(
            "https://api.ariba.com/v2/oauth/token",
            headers={
                "Authorization": f"Basic {self.base64_encoded_secret_key}"
            },
            data={
                "grant_type": "client_credentials",
            },
        )
        if response.status_code == 401:
            raise AribaAuthWrongCredentialError(response=response)

        response.raise_for_status()
        data = response.json()

        if _should_close_client:
            await client.aclose()

        return AribaOAuthToken(
            date_created=timezone.now(),
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_in=data["expires_in"],
        )

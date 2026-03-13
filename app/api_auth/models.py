import hashlib
import secrets
from base64 import urlsafe_b64encode
from datetime import datetime
from functools import lru_cache
from hmac import compare_digest
from typing import Any, Iterable

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpRequest
from django.utils import timezone

from app.helpers.network import get_ip_from_request
from app.models.base import UUIDModel


class APIScopes(UUIDModel):
    slug = models.CharField[str, str](max_length=64)
    description = models.TextField[str, str](blank=True)
    is_active = models.BooleanField[bool, bool](default=True)

    class Meta:  # type: ignore[override]
        verbose_name = "API Scope"
        verbose_name_plural = "API Scopes"
        constraints = [
            models.UniqueConstraint(
                fields=["slug"],
                name="api_scope_slug_unique",
            )
        ]

    def __str__(self) -> str:
        return self.slug


@lru_cache(maxsize=1)
def _get_cipher() -> Fernet:
    key_material = settings.SECRET_KEY.encode("utf-8")
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"app.api_auth.models.APIKey",
        info=b"api-key-encryption",
    ).derive(key_material)
    return Fernet(urlsafe_b64encode(derived_key))


class APIKey(UUIDModel):
    name = models.CharField[str, str](max_length=255)
    description = models.TextField[str, str](blank=True)
    key = models.TextField[str, str](editable=False, default="")
    key_prefix = models.CharField[str, str](
        max_length=12,
        editable=False,
        default="",
    )
    key_hash = models.CharField[str, str](
        max_length=64,
        editable=False,
        default="",
    )
    allowed_solutions = models.ManyToManyField[APIScopes, APIScopes](
        to=APIScopes,
        blank=True,
        related_name="+",
    )
    is_active = models.BooleanField[bool, bool](default=True)
    created_at = models.DateTimeField[datetime, datetime](auto_now_add=True)
    expires_at = models.DateTimeField[datetime | None, datetime | None](
        blank=True,
        null=True,
    )
    revoked_at = models.DateTimeField[datetime | None, datetime | None](
        blank=True,
        null=True,
    )
    last_used_at = models.DateTimeField[datetime | None, datetime | None](
        blank=True,
        null=True,
    )
    last_used_ip = models.GenericIPAddressField[str | None, str | None](
        blank=True,
        null=True,
    )

    class Meta:  # type: ignore[override]
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
        constraints = [
            models.UniqueConstraint(
                fields=["key_hash"],
                name="api_key_key_hash_unique",
            ),
            models.UniqueConstraint(
                fields=["name"],
                name="api_key_name_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["key_prefix"],
                name="api_key_prefix_index",
            ),
        ]

    @staticmethod
    def get_key_hash(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @staticmethod
    def get_key_prefix(raw_key: str) -> str:
        return raw_key[:12]

    @staticmethod
    def encrypt_key(raw_key: str) -> str:
        return _get_cipher().encrypt(raw_key.encode("utf-8")).decode("utf-8")

    @staticmethod
    def decrypt_key(encrypted_key: str) -> str:
        try:
            decrypted_key = _get_cipher().decrypt(
                encrypted_key.encode("utf-8")
            )
        except InvalidToken as error:
            if encrypted_key.startswith("sk_"):
                return encrypted_key
            raise ValidationError("Stored API key is invalid") from error
        return decrypted_key.decode("utf-8")

    def set_raw_key(self, raw_key: str) -> None:
        self.key = self.encrypt_key(raw_key)
        self.key_prefix = self.get_key_prefix(raw_key)
        self.key_hash = self.get_key_hash(raw_key)

    def generate_key(self, *, commit: bool = True) -> str:
        raw_key = "sk_" + secrets.token_hex(16)
        self.set_raw_key(raw_key)
        if commit:
            self.save()
        return raw_key

    def save(self, *args: Any, **kwargs: Any) -> None:
        generated_fields: list[str] = []
        if not self.key:
            self.set_raw_key("sk_" + secrets.token_hex(16))
            generated_fields = ["key", "key_prefix", "key_hash"]
        elif not self.key_prefix or not self.key_hash:
            self.set_raw_key(self.get_raw_key())
            generated_fields = ["key", "key_prefix", "key_hash"]

        update_fields = kwargs.get("update_fields")
        if update_fields is not None and generated_fields:
            existing_fields: list[str] = list(
                update_fields
                if isinstance(update_fields, Iterable)
                else [str(update_fields)]
            )
            kwargs["update_fields"] = [*existing_fields, *generated_fields]

        super().save(*args, **kwargs)

    def get_raw_key(self) -> str:
        return self.decrypt_key(self.key)

    def verify_key(self, raw_key: str) -> bool:
        return compare_digest(self.key_hash, self.get_key_hash(raw_key))

    def is_expired(self, *, at: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False
        check_at = at or timezone.now()
        return check_at >= self.expires_at

    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def can_authenticate(self, *, at: datetime | None = None) -> bool:
        return (
            self.is_active
            and not self.is_revoked()
            and not self.is_expired(at=at)
        )

    def mark_used(self, *, request: HttpRequest, commit: bool = True) -> None:
        self.last_used_at = timezone.now()
        self.last_used_ip = get_ip_from_request(request=request)
        if commit:
            self.save(update_fields=["last_used_at", "last_used_ip"])

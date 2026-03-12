import secrets

from django.db import models

from app.models.base import UUIDModel


class APISolution(UUIDModel):
    name = models.CharField[str, str](max_length=255)
    description = models.TextField[str, str](blank=True)

    class Meta:
        verbose_name = "API Solutions"
        verbose_name_plural = "API Solutions"
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="api_solution_name_unique",
            )
        ]

    def __str__(self) -> str:
        return self.name


class APIKey(UUIDModel):
    name = models.CharField[str, str](max_length=255)
    description = models.TextField[str, str](blank=True)
    key = models.CharField[str, str](max_length=36)
    allowed_solutions = models.ManyToManyField[APISolution, APISolution](
        to=APISolution,
        blank=True,
        null=True,
        related_name="+",
    )
    is_active = models.BooleanField[bool, bool](default=True)

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
        constraints = [
            models.UniqueConstraint(
                fields=["key"],
                name="api_key_key_unique",
            ),
            models.UniqueConstraint(
                fields=["name"],
                name="api_key_name_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["key"],
                name="api_key_key_index",
            ),
        ]

    def generate_key(self, *, commit: bool = True) -> str:
        self.key = "sk_" + secrets.token_hex(16)
        if commit:
            self.save()
        return self.key

from django.db import models

from app.models.base import UUIDModel


class ValidShipToAddress(UUIDModel):
    name = models.CharField[str, str](max_length=255, unique=True)
    street = models.CharField[str, str](max_length=255)
    city = models.CharField[str, str](max_length=255)
    state = models.CharField[str, str](max_length=255)
    country = models.CharField[str, str](max_length=255)
    postal_code = models.CharField[str, str](max_length=255)

    def __str__(self) -> str:
        return self.name

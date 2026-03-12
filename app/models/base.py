import uuid
from datetime import datetime

from django.db import models


class TimeStampedModel(models.Model):
    created_at: models.DateTimeField[datetime, datetime](auto_now_add=True)
    modified_at = models.DateTimeField[datetime, datetime](auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    internal_id = models.AutoField[int, int](
        primary_key=True,
        editable=False,
    )
    id = models.UUIDField[uuid.UUID, uuid.UUID](
        unique=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )

    class Meta:
        abstract = True


class TimestampedUUIDModel(TimeStampedModel, UUIDModel):
    class Meta(TimeStampedModel.Meta, UUIDModel.Meta):
        abstract = True

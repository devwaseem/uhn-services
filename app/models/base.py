import uuid

from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    internal_id = models.AutoField(primary_key=True, editable=False)
    id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )

    class Meta:
        abstract = True

class TimestampedUUIDModel(TimeStampedModel, UUIDModel):
    class Meta:
        abstract = True

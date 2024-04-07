from uuid import uuid4

from django.db import models


class UuidModel(models.Model):
    """Model with a UUID an `uuid` field that can be used as a secondary primary key."""

    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["uuid"])]

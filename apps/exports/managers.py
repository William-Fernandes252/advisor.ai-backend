from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.db import models

if TYPE_CHECKING:
    from apps.exports.models import Export


class ExportManager(models.Manager):
    def get_latest_for_content_type(self, content_type: ContentType) -> "Export":
        """Return the latest export for a given content type.

        Args:
            content_type (ContentType): The content type to filter by.

        Returns:
            Export: The corresponding export.
        """
        return self.filter(content_type=content_type, latest=True).first()  # type: ignore[return-value]

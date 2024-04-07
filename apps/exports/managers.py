from django.contrib.contenttypes.models import ContentType
from django.db import models


class ExportManager(models.Manager):
    def get_latest_for_content_type(self, content_type: ContentType):
        """Return the latest export for a given content type.

        Args:
            content_type (ContentType): The content type to filter by.

        Returns:
            Export: The corresponding export.
        """
        return self.filter(content_type=content_type, latest=True).first()

import csv
import pathlib
import tempfile
import uuid
from collections.abc import Iterable
from typing import Any, Self

from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.db import models
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel

from apps.exports import managers
from apps.exports.utils import save


def export_file_handler(instance: "Export", filename):
    ext = pathlib.Path(filename).suffix
    if hasattr(instance, "id"):
        new_filename = f"{instance.id}{ext}"
    else:
        new_filename = f"{uuid.uuid4()}{ext}"

    base = pathlib.Path("exports")
    if (
        instance.content_type
        and (model_type := instance.content_type.model_class())
        and (meta := model_type._meta) is not None  # noqa: SLF001
    ):
        base /= str(meta.model_name or "")

    return base / timezone.now().strftime("%Y-%m-%d") / new_filename


class Export(TimeStampedModel, models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    file = models.FileField(blank=True, null=True, upload_to=export_file_handler)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
    )
    latest = models.BooleanField(default=True)

    objects: managers.ExportManager = managers.ExportManager()

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.latest and self.file:
            path = export_file_handler(self, self.filename)
            folder = path.parent.parent
            save(folder / f"latest{path.suffix}", self.file, overwrite=True)
            Export.objects.filter(content_type=self.content_type).exclude(
                pk=self.pk
            ).update(latest=False)

    @property
    def filename(self):
        return pathlib.Path(self.file.name).name

    def delete(self, *args, **kwargs):
        if self.file and self.file.storage.exists(self.file.name):
            self.file.delete(save=False)
        super().delete(*args, **kwargs)

    @classmethod
    def from_dataset(
        cls,
        dataset: Iterable[Any],
        fieldnames: list[str],
        filename: str,
        content_type: ContentType | None = None,
    ) -> Self:
        """Exports a dataset to a CSV file.

        Args:
            dataset (list[dict[str, Any]]): The dataset to export.
            fieldnames (list[str]): The field names of the dataset.
            filename (str): A name for the destination file.
            content_type (ContentType | None, optional): The content type of the
            dataset model. Defaults to None.

        Returns:
            Export: The created export instance.
        """
        with tempfile.NamedTemporaryFile(mode="r+") as tmp:
            writer = csv.DictWriter(tmp, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(dataset)
            tmp.seek(0)
            export: Export = Export.objects.create(content_type=content_type)
            export.file.save((filename + ".csv"), File(tmp))
            return export

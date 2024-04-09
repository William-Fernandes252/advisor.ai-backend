import pathlib
import uuid
from typing import Any

import pandas as pd
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from apps.exports.utils import save
from apps.ml import managers
from apps.ml.encoders import ValidationResultsJSONEncoder


def model_file_handler(instance: "Model", filename):
    return (
        pathlib.Path("ml")
        / "models"
        / instance.type
        / timezone.now().strftime("%Y-%m-%d")
        / filename
    )


class Model(TimeStampedModel, models.Model):
    """Model for storing machine learning models."""

    class TypeChoices(models.TextChoices):
        SVD = "svd", "SVD"

    _model: Any | None = None

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    file = models.FileField(blank=True, null=True, upload_to=model_file_handler)
    latest = models.BooleanField(default=True)
    type = models.CharField(max_length=3, choices=TypeChoices.choices)
    params = models.JSONField(
        help_text=_("Parameters for training"), encoder=DjangoJSONEncoder, null=True
    )
    validation_results = models.JSONField(
        encoder=ValidationResultsJSONEncoder, null=True
    )

    objects: managers.ModelManager = managers.ModelManager()

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.filename + " - " + self.type

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.latest and self.file:
            path = model_file_handler(self, self.filename)
            folder = path.parent.parent
            save(folder / f"latest{path.suffix}", self.file, overwrite=True)
            Model.objects.filter(type=self.type).exclude(pk=self.pk).update(
                latest=False
            )

    @property
    def filename(self):
        return pathlib.Path(self.file.name).name

    def delete(self, *args, **kwargs):
        if self.file and self.file.storage.exists(self.file.name):
            self.file.delete(save=False)
        super().delete(*args, **kwargs)

    def train(self, df: pd.DataFrame) -> None:
        """Train the model using the provided dataset.

        Args:
            df (pandas.DataFrame): The dataset to train the model on.
        """
        raise NotImplementedError

    def persist(self) -> None:
        """Persist the model to the file."""
        raise NotImplementedError

    def prepare_for_training(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare the dataset for training.

        Args:
            df (pandas.DataFrame): The base dataset.

        Returns:
            pandas.DataFrame: The resulting dataset.
        """
        raise NotImplementedError

    def load(self) -> None:
        """Load the model from the file."""
        raise NotImplementedError

    def predict(self, user_id: int, paper_id: int) -> float:
        """Predict the ratings for the provided dataset.

        Args:
            user_id (int): The user ID.
            paper_id (int): The paper ID.

        Returns:
            float: The predicted rating.
        """
        raise NotImplementedError

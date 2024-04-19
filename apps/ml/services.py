from typing import Final

import pandas as pd
from django.contrib.contenttypes.models import ContentType
from django.utils.module_loading import import_string

from apps.exports.models import Export
from apps.ml.models import Model
from apps.papers.models import Paper
from apps.reviews.models import Review

MODEL_TYPE_TO_CLASS: Final[dict[Model.TypeChoices, str]] = {
    Model.TypeChoices.SVD: "SVDModel",
}


def _import_model_class(model_type: Model.TypeChoices) -> type[Model]:
    """Imports the model class for the provided type.

    Note that it can raise an ImportError if the dependency groups of the class
    dependencies are not installed.

    Args:
        model_type (Model.TypeChoices): The type of the model.

    Returns:
        type[Model]: The model class.
    """
    return import_string(f"apps.ml.models.{MODEL_TYPE_TO_CLASS[model_type]}")


def import_paper_reviews_dataset() -> pd.DataFrame:
    """Imports the papers ratings dataset and joins it with the papers dataset."""
    papers_latest_export: Export | None = Export.objects.get_latest_for_content_type(
        ContentType.objects.get_for_model(Paper)
    )
    if (papers_latest_export is None) or not papers_latest_export.file.storage.exists(
        papers_latest_export.file.name
    ):
        msg = "No paper dataset found."
        raise ValueError(msg)

    reviews_latest_export: Export | None = Export.objects.get_latest_for_content_type(
        ContentType.objects.get_for_model(Review)
    )
    if (reviews_latest_export is None) or not reviews_latest_export.file.storage.exists(
        reviews_latest_export.file.name
    ):
        msg = "No ratings dataset found."
        raise ValueError(msg)

    papers_df = pd.read_csv(papers_latest_export.file)
    reviews_df = pd.read_csv(reviews_latest_export.file)

    return reviews_df.copy().join(
        papers_df, on="paperId", rsuffix="_paper_df", how="inner"
    )


def train_and_export_model(
    model_type: Model.TypeChoices, params: dict | None = None
) -> Model:
    """Trains a model and exports it.

    Args:
        model_type (Model.TypeChoices): The type of the model to train.
        params (dict | None, optional): The training params.
        Each model has its own set of params.
        If not provided, the default params will be used.

    Returns:
        Model: The trained model.
    """
    reviews_df = import_paper_reviews_dataset()

    model: Model = _import_model_class(model_type)(params=params)
    model.train(reviews_df)
    model.persist()
    model.save()

    return model


def load_latest_model(model_type: Model.TypeChoices) -> Model:
    """Loads the latest model of the provided type.

    Args:
        model_type (Model.TypeChoices): The type of the model to load.

    Returns:
        Model: The loaded model.
    """
    model_class: type[Model] = _import_model_class(model_type)
    model: Model = model_class.objects.get_latest_for_type(model_type)
    model.load()
    return model

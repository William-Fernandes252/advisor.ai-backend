"""Proxies to manage models trained using the scikit-surprise library."""

import pickle
import tempfile
from typing import Any, ClassVar, override

import pandas as pd
from django.core.files import File
from surprise import SVD, Dataset, Reader
from surprise.accuracy import rmse
from surprise.model_selection import cross_validate

from apps.ml.models.base import Model


class SVDModel(Model):
    """Model for storing SVD models."""

    _model: SVD | None = None

    DEFAULT_PARAMS: ClassVar[dict[str, Any]] = {
        "n_epochs": 20,
        "lr_all": 0.005,
        "reg_all": 0.02,
        "verbose": True,
    }

    class Meta:
        proxy = True
        verbose_name = "SVD Model"
        verbose_name_plural = "SVD Models"

    @override
    def __init__(self, *args, **kwargs) -> None:
        """Initializes the SVD model by setting defaults."""
        super().__init__(*args, **kwargs)
        self.type = Model.TypeChoices.SVD
        if not self.params:
            self.params = self.DEFAULT_PARAMS

    @override
    def prepare_for_training(self, df: pd.DataFrame) -> pd.DataFrame:
        training_df = df.copy().dropna(subset=["userId", "paperId", "rating"])

        for column, column_type in [
            ("userId", int),
            ("paperId", int),
            ("paperIndex", int),
            ("rating", float),
        ]:
            training_df[column] = training_df[column].astype(column_type)

        return training_df.rename(
            columns={"userId": "user", "paperIndex": "paper", "rating": "rating"}
        )

    @staticmethod
    def _get_data_loader(dataset_as_df: pd.DataFrame):
        """Loads a dataset into a Surprise DatasetAutoFolds object.

        Args:
            dataset_as_df (pandas.DataFrame): The dataset to load.
            It must contain the columns:
            - user: The users IDs.
            - paper: The papers IDs.
            - rating: The ratings.

        Returns:
            dataset.DatasetAutoFolds: The loaded dataset.
        """
        reader = Reader(
            rating_scale=(dataset_as_df["rating"].max(), dataset_as_df["rating"].min())
        )
        return Dataset.load_from_df(dataset_as_df[["user", "paper", "rating"]], reader)

    @override
    def persist(self) -> None:
        with tempfile.NamedTemporaryFile("rb+") as temp:
            pickle.dump(self.model, temp)
            self.file.save(
                self.get_name_for_file(),
                File(temp),
                save=True,
            )

    def get_accuracy(self) -> float | None:
        """Return the RMSE based accuracy of the model."""
        if not self.model:
            return None
        return rmse(self.model.test(self.model.trainset.build_testset()))

    def get_name_for_file(self) -> str | None:
        """Return the name for the model file."""
        if not self.model:
            return None
        return f"model-{100 * int(self.get_accuracy() or 0)}.pkl"

    @override
    def train(self, df: pd.DataFrame) -> None:
        training_df = self.prepare_for_training(df)
        data = self._get_data_loader(training_df)

        self.model = SVD(**self.params)
        self.validation_results = cross_validate(
            self.model, data, measures=["RMSE", "MAE"], cv=4, verbose=True
        )

        trainset = data.build_full_trainset()
        self.model.fit(trainset)

    @override
    def load(self) -> None:
        if not self.file or not self.file.storage.exists(self.file.name):
            msg = "No model file found."
            raise ValueError(msg)

        with self.file.open("rb") as f:
            self._model = pickle.load(f)  # noqa: S301

    @override
    def predict(self, user_id: int, paper_id: int) -> float:
        if self._model is None:
            self.load()

        return self._model.predict(user_id, paper_id).est  # type: ignore[union-attr]

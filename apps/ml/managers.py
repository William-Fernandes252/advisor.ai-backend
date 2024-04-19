from django.db import models


class ModelManager(models.Manager):
    """Manager for the machine learning model objects."""

    def get_latest_for_type(self, model_type):
        """Return the latest model for a given type.

        Args:
            model_type (str): The model type to filter by.

        Returns:
            Model: The corresponding model.
        """
        return self.filter(type=model_type, latest=True).order_by("-created").first()

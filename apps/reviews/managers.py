from django.db import models

from apps.reviews.querysets import ReviewQuerySet


class ReviewManager(models.Manager):
    """Manager for the Review model."""

    def get_queryset(self):
        return ReviewQuerySet(self.model, using=self._db)

    def active(self):
        """Return only active reviews."""
        return self.get_queryset().active()

    def inactive(self):
        """Return only inactive reviews."""
        return self.get_queryset().inactive()

    def average(self):
        return self.get_queryset().average()

    def to_dataset(self) -> models.QuerySet:
        """Generates a dataset with the active reviews.

        The dataset is generated as a values queryset with the following columns:
        - userId
        - paperId
        - rating
        - createdAt

        Returns:
            QuerySet: The ratings dataset (as a values queryset) for the given model.
        """
        return (
            self.active()
            .annotate(
                **{  # noqa: PIE804
                    "userId": models.F("user_id"),
                    "paperId": models.F("paper_id"),
                    "rating": models.F("value"),
                    "createdAt": models.F("created"),
                }
            )
            .values("userId", "paperId", "rating", "createdAt")
        )

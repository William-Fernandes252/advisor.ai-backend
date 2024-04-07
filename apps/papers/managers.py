from django.db import models

from apps.papers import querysets


class PaperManager(models.Manager):
    def get_queryset(self) -> querysets.PaperQuerySet:
        return querysets.PaperQuerySet(self.model, using=self._db)

    def outdated_rating(self) -> querysets.PaperQuerySet:
        """Return papers with outdated rating data."""
        return self.get_queryset().filter_outdated_reviews()

    def popular(self, reverse) -> querysets.PaperQuerySet:
        """Return papers ordered by popularity."""
        return self.get_queryset().popular_on_demand(reverse=reverse)

    def to_dataset(self) -> models.QuerySet:
        """Generates a dataset with the papers data.

        The dataset is generated as a values queryset with the following columns:
        - paperId
        - paperIndex
        - title
        - publishedAt
        - reviewsAverage
        - reviewsCount

        Returns:
            QuerySet: The papers dataset.
        """
        return (
            self.get_queryset()
            .annotate(
                **{  # noqa: PIE804
                    "paperId": models.F("pk"),
                    "paperIndex": models.F("index"),
                    "publishedAt": models.F("published"),
                    "reviewsAverage": models.F("reviews_average"),
                    "reviewsCount": models.F("reviews_count"),
                }
            )
            .values(
                "paperId",
                "paperIndex",
                "title",
                "publishedAt",
                "reviewsAverage",
                "reviewsCount",
            )
        )

from django.db import models

from apps.papers import querysets
from apps.suggestions.models import Suggestion


class PaperManager(models.Manager):
    """Manager for the Paper model."""

    def get_queryset(self) -> querysets.PaperQuerySet:
        return querysets.PaperQuerySet(self.model, using=self._db)

    def outdated_rating(self) -> querysets.PaperQuerySet:
        """Return papers with outdated rating data."""
        return self.get_queryset().filter_outdated_reviews()

    def popular(self, reverse=None) -> querysets.PaperQuerySet:
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

    def recent_suggestions(
        self,
        users_ids: list[int],
        papers_ids: list[int],
        days: int = 7,
    ) -> dict[int, list[int]]:
        """Returns the recent suggestions for the given users and movies.

        Args:
            users_ids (list[int]): The IDs of the users.
            papers_ids (list[int]): The IDs of the papers.
            days (int, optional): Days to consider. Defaults to 7.

        Returns:
            dict[int, list[int]]: A dictionary mapping papers to the users each paper
            was suggested to.
        """
        data: dict[int, list[int]] = {}
        for item in Suggestion.objects.recent(
            papers_ids=papers_ids,
            users_ids=users_ids,
            days=days,
        ).values("paper_id", "user_id"):
            if item["paper_id"] not in data:
                data[item["paper_id"]] = []
            data[item["paper_id"]].append(item["user_id"])
        return data

    def order_by_ids(self, ids: list[int]) -> querysets.PaperQuerySet:
        """Orders the queryset by the given IDs.

        Args:
            ids (list[int]): The IDs to order by.

        Returns:
            QuerySet: The ordered queryset.
        """
        return (
            self.get_queryset()
            .filter(pk__in=ids)
            .order_by(
                models.Case(
                    *[models.When(pk=pk, then=pos) for pos, pk in enumerate(ids)]
                )
            )
        )

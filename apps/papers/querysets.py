from typing import Self

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import models
from django.utils import timezone

PAPERS_REVIEWS_RECALCULATE_MINUTES = 10


class PaperQuerySet(models.QuerySet):
    def search(self, value: str) -> Self:
        """Search for papers.

        Args:
            query (str): The term to search for. It will be searched in the title
            and abstract of the papers.

        Returns:
            QuerySet: A queryset with the search results ordered by the
            rank of the search.
        """
        vector = SearchVector("title") + SearchVector("abstract")
        query = SearchQuery(value)
        return self.annotate(rank=SearchRank(vector, query)).order_by("-rank")

    def filter_outdated_reviews(self):
        """Filter papers with outdated reviews data."""
        now = timezone.now()
        return self.filter(
            models.Q(reviews_last_updated__isnull=True)
            | models.Q(
                reviews_last_updated__lte=now
                - timezone.timedelta(minutes=PAPERS_REVIEWS_RECALCULATE_MINUTES)
            )
        )

    def popular(self, reverse):
        """Order the papers by popularity."""
        order_by = models.F("score")
        if not reverse:
            order_by = order_by.desc(nulls_last=True)
        return self.order_by(order_by)

    def popular_on_demand(self, reverse):
        """Order the papers by their current popularity."""
        order_by = models.F("computed_score")
        if not reverse:
            order_by = order_by.desc(nulls_last=True)
        return self.annotate(
            computed_score=models.Sum(
                models.F("reviews_average") * models.F("reviews_count"),
                output_field=models.FloatField(),
            ),
        ).order_by(order_by)

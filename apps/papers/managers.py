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

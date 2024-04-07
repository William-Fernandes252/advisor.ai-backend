from django.db import models

from apps.reviews.querysets import ReviewQuerySet


class ReviewManager(models.Manager):
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

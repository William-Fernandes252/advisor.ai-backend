from django.db import models
from django.utils import timezone


class SuggestionManager(models.Manager):
    def recent(
        self,
        papers_ids: list[int],
        users_ids: list[int],
        days: int = 7,
    ):
        """Return recently created suggestions of the specified papers
        for the given users.

        Args:
            papers_ids (list[int]): The papers IDs.
            users_ids (list[int]): The users IDs.
            days (int, optional): The number of days to consider. Defaults to 7.

        Returns:
            QuerySet: The suggestions queryset.
        """
        return self.get_queryset().filter(
            paper_id__in=papers_ids,
            user_id__in=users_ids,
            active=True,
            created__gte=timezone.now() - timezone.timedelta(days=days),
        )

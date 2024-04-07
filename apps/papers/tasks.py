from celery import shared_task
from django.db.models import Avg, Count
from django.utils import timezone

from apps.papers import models
from apps.reviews.models import Review


def update_paper_reviews(update_all=None, count: int | None = None):
    """Updates papers reviews data (average and count).

    Args:
        update_all (bool, optional): If True, all the papers in the database are
        updated, only papers with outdated reviews information are updated otherwise.
        Defaults to all.
        count (int, optional): The number of papers to update. Defaults to None.

    Returns:
        int: The number of papers updated.
    """

    aggregated_reviews = (
        Review.objects.all()
        .values("paper_id")
        .annotate(average=Avg("value"), count=Count("paper_id"))
    )

    queryset = models.Paper.objects.get_queryset().order_by("reviews_last_updated")
    if not update_all:
        queryset = queryset.filter_outdated_reviews()

    updated = 0
    for agg in aggregated_reviews:
        queryset.filter(pk=agg["paper_id"]).update(
            reviews_average=agg["average"],
            reviews_count=agg["count"],
            score=agg["average"] * agg["count"],
            reviews_last_updated=timezone.now(),
        )
        updated += 1
        if count and updated >= count:
            break
    return updated


@shared_task(name="update_paper_reviews_outdated")
def update_paper_reviews_outdated():
    """Updates outdated papers reviews data."""
    return update_paper_reviews()

from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count, F, Window
from django.db.models.functions import DenseRank
from django.utils import timezone

from apps.exports.models import Export
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

    queryset = models.Paper.objects.get_queryset().order_by("last_reviews_update")
    if not update_all:
        queryset = queryset.filter_outdated_reviews()

    updated = 0
    for agg in aggregated_reviews:
        queryset.filter(pk=agg["paper_id"]).update(
            reviews_average=agg["average"],
            reviews_count=agg["count"],
            score=agg["average"] * agg["count"],
            last_reviews_update=timezone.now(),
        )
        updated += 1
        if count and updated >= count:
            break
    return updated


@shared_task(name="update_paper_reviews_outdated")
def update_paper_reviews_outdated():
    """Updates outdated papers reviews data."""
    return update_paper_reviews()


@shared_task(name="export_paper_reviews_dataset")
def export_paper_reviews_dataset(filename: str | None = None) -> str | None:
    """Exports a dataset with the papers reviews, average and count.

    Args:
        filename (str | None, optional): A name for the destination file.
        Defaults to `paper_reviews`.

    Returns:
        str: The export file path.
    """
    return Export.from_dataset(
        Review.objects.to_dataset(),
        fieldnames=["userId", "paperId", "rating", "createdAt"],
        filename=filename or "paper_reviews",
        content_type=ContentType.objects.get_for_model(Review),
    ).file.path


@shared_task(name="export_papers_dataset")
def export_papers_dataset():
    """Exports a dataset with the papers data.

    Returns:
        str: The export file path.
    """
    return Export.from_dataset(
        models.Paper.objects.to_dataset(),
        fieldnames=[
            "paperId",
            "paperIndex",
            "title",
            "publishedAt",
            "reviewsAverage",
            "reviewsCount",
        ],
        filename="papers",
        content_type=ContentType.objects.get_for_model(models.Paper),
    ).file.path


@shared_task(name="update_papers_position_embeddings")
def update_papers_position_embeddings():
    """Update the papers embeddings.

    Returns:
        int: The number of papers updated.
    """
    updated = 0
    for paper in (
        models.Paper.objects.all()
        .annotate(embedding_index=Window(DenseRank(), order_by=[F("id").asc()]))
        .annotate(new_index=F("embedding_index") - 1)
    ):
        if paper.index != getattr(paper, "new_index", None):
            paper.index = getattr(paper, "new_index", None)
            paper.save()
            updated += 1
    return updated

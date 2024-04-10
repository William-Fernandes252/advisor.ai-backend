from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count, F, Window
from django.db.models.functions import DenseRank
from django.utils import timezone

from apps.exports.models import Export
from apps.ml import services
from apps.ml.models import Model
from apps.papers import models
from apps.reviews.models import Review
from apps.suggestions.models import Suggestion
from apps.users.models import User


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


@shared_task(name="train_and_export_new_model")
def train_and_export_new_model(model_type, params: dict | None = None):
    """Trains and exports a new model.

    Args:
        model_type (str): The model type to train.
        params (dict | None, optional): The training params. Defaults to None.

    Returns:
        str: The export file path.
    """
    return services.train_and_export_model(
        model_type=model_type, params=params
    ).file.path


@shared_task(name="batch_create_papers_suggestions")
def batch_create_papers_suggestions(  # noqa: PLR0913
    model_type: Model.TypeChoices,
    users_ids: list[int] | None = None,
    *,
    max_papers: int = 1000,
    offset: int = 50,
    start: int = 0,
    use_suggestions_up_to_days: int | None = 7,
):
    """Generates suggestions for a batch of users.

    Args:
        model_type (str): The model type to use.
        users_ids (list[int] | None, optional): The users to generate suggestions to.
        Defaults to the users that interacted with the application recently.
        max_papers (int, optional): The maximum number of papers to generate suggestions.
        Defaults to 1000.
        offset (int, optional): The number of papers to generate suggestions at a time.
        Defaults to 50.
        start (int, optional): The papers start index. Defaults to 0.
        use_suggestions_up_to_days (int | None, optional): Reuse suggestions up to the given days.
        Defaults to 7.

    Raises:
        ValueError: If the model is not found.
    """  # noqa: E501

    model = services.load_latest_model(model_type)
    if not model:
        msg = "Model not found."
        raise ValueError(msg)

    if users_ids is None:
        users_ids = User.objects.recent(ids_only=True)  # type: ignore[assignment]

    end = start + offset
    papers_ids: list[int] = (
        models.Paper.objects.all().popular().values_list("id", flat=True)[start:end]
    )

    recent_suggestions = {}
    if use_suggestions_up_to_days:
        recent_suggestions = models.Paper.objects.recent_suggestions(
            users_ids,  # type: ignore[arg-type]
            papers_ids,
            days=use_suggestions_up_to_days,
        )

    count = 0
    while count < max_papers:
        suggestions: list[Suggestion] = []
        for paper_id in papers_ids:
            users_covered = recent_suggestions.get(paper_id, [])
            for user_id in users_ids or []:
                if user_id in users_covered:
                    continue
                suggestions.append(
                    Suggestion(
                        user_id=user_id,
                        paper_id=paper_id,
                        value=model.predict(user_id, paper_id),
                        model=model,
                    )
                )
            count += 1

        Suggestion.objects.bulk_create(suggestions)

        start += offset
        end = start + offset
        papers_ids = (
            models.Paper.objects.all()
            .popular()
            .values_list("id", flat=True)[start : start + offset]
        )


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

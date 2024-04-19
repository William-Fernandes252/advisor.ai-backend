from apps.reviews import models, querysets
from apps.suggestions.models import Suggestion


def deactivate_old_ratings(
    sender: type[models.Review], instance: models.Review, created, **kwargs
):
    """Deactivate users old reviews for a paper when a new one is created."""
    if created:
        if instance.active:
            old_ratings_queryset: querysets.ReviewQuerySet = (
                models.Review.objects.get_queryset()
                .filter(
                    user=instance.user,
                    paper=instance.paper,
                )
                .exclude(pk=instance.pk, active=True)
            )
            if old_ratings_queryset.exists():
                old_ratings_queryset.deactivate()
                instance.active = True
                instance.save()
        if (
            suggestion_queryset := Suggestion.objects.filter(
                user=instance.user,
                paper=instance.paper,
                review__isnull=True,
            )
        ).exists():
            suggestion_queryset.update(review=instance)

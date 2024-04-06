from apps.reviews import models, querysets


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

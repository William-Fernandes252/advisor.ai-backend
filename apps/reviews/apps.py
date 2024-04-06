from django.apps import AppConfig
from django.db.models.signals import post_save


class ReviewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reviews"

    def ready(self) -> None:
        super().ready()

        from apps.reviews import models, signals

        post_save.connect(
            signals.deactivate_old_ratings,
            sender=models.Rating,
            dispatch_uid="deactivate_old_ratings",
        )

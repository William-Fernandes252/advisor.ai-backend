from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save
from django.utils.translation import gettext_lazy as _


class PapersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.papers"
    verbose_name = _("Papers")

    def ready(self):
        from apps.papers import models, signals

        post_save.connect(
            signals.recalculate_papers_embeddings_on_save,
            sender=models.Paper,
            dispatch_uid="recalculate_papers_embeddings_on_save",
        )
        post_delete.connect(
            signals.recalculate_papers_embeddings_on_delete,
            sender=models.Paper,
            dispatch_uid="recalculate_papers_embeddings_on_delete",
        )
